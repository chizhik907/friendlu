# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# ========== БАЗА ДАННЫХ ==========
def get_db():
    conn = sqlite3.connect('dating.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        gender TEXT,
        age INTEGER,
        city TEXT,
        bio TEXT,
        photo TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user_id INTEGER,
        to_user_id INTEGER,
        UNIQUE(from_user_id, to_user_id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user_id INTEGER,
        to_user_id INTEGER,
        text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        test = [
            ('Анна', '123', 'female', 24, 'Москва', 'Люблю кофе', 'https://i.pravatar.cc/400?img=1'),
            ('Мария', '123', 'female', 22, 'Казань', 'Спорт', 'https://i.pravatar.cc/400?img=10'),
            ('Дмитрий', '123', 'male', 26, 'Москва', 'Программист', 'https://i.pravatar.cc/400?img=11'),
            ('Алексей', '123', 'male', 30, 'Сочи', 'Активный', 'https://i.pravatar.cc/400?img=12'),
        ]
        for u in test:
            c.execute('INSERT INTO users (username, password, gender, age, city, bio, photo) VALUES (?,?,?,?,?,?,?)', u)
        print('👥 Добавлено 4 тестовых пользователя (пароль: 123)')
    
    conn.commit()
    conn.close()
    print('✅ База данных готова')

init_db()

# ========== ГЛАВНАЯ ==========
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'ok',
        'message': '❤️ Сервер знакомств работает!',
        'users_count': 4,
        'test_users': ['Анна', 'Мария', 'Дмитрий', 'Алексей'],
        'test_password': '123'
    })

# ========== РЕГИСТРАЦИЯ ==========
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    print('📝 Регистрация:', data['username'])
    
    conn = get_db()
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO users (username, password, gender, age, city, bio, photo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['username'],
            data['password'],  # БЕЗ ХЭШИРОВАНИЯ!
            data['gender'],
            int(data['age']),
            data['city'],
            data.get('bio', 'Люблю знакомиться!'),
            data.get('photo', 'https://i.pravatar.cc/400?img=' + str(abs(hash(data['username'])) % 70))
        ))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return jsonify({'success': True, 'user_id': user_id}), 201
    except Exception as e:
        conn.close()
        print('❌ Ошибка:', e)
        return jsonify({'error': 'Пользователь уже существует'}), 400

# ========== ВХОД ==========
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    print('🔑 Вход:', data['username'])
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (data['username'],))
    user = c.fetchone()
    conn.close()
    
    if not user:
        print('❌ Пользователь не найден')
        return jsonify({'error': 'Пользователь не найден'}), 401
    
    print(f'📝 Пароль в БД: {user["password"]}')
    print(f'📝 Введенный пароль: {data["password"]}')
    
    if user['password'] == data['password']:
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'gender': user['gender'],
                'age': user['age'],
                'city': user['city'],
                'bio': user['bio'],
                'photo': user['photo']
            }
        }), 200
    else:
        print('❌ Пароли не совпадают')
        return jsonify({'error': 'Неверный пароль'}), 401

# ========== ДОСТУПНЫЕ АНКЕТЫ ==========
@app.route('/api/users/<int:user_id>/available', methods=['GET'])
def get_available(user_id):
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT gender FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    target = 'female' if user['gender'] == 'male' else 'male'
    
    c.execute('SELECT to_user_id FROM likes WHERE from_user_id = ?', (user_id,))
    liked = [row['to_user_id'] for row in c.fetchall()]
    
    query = 'SELECT * FROM users WHERE id != ? AND gender = ?'
    params = [user_id, target]
    if liked:
        query += ' AND id NOT IN (' + ','.join(['?'] * len(liked)) + ')'
        params.extend(liked)
    
    c.execute(query, params)
    users = []
    for row in c.fetchall():
        u = dict(row)
        u.pop('password', None)
        users.append(u)
    
    conn.close()
    return jsonify({'users': users})

# ========== ЛАЙК ==========
@app.route('/api/likes', methods=['POST'])
def add_like():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    
    try:
        c.execute('INSERT INTO likes (from_user_id, to_user_id) VALUES (?, ?)',
                 (data['from_user_id'], data['to_user_id']))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'is_mutual': False})
    except:
        conn.close()
        return jsonify({'error': 'Already liked'}), 400

# ========== ВЗАИМНЫЕ СИМПАТИИ ==========
@app.route('/api/users/<int:user_id>/mutual', methods=['GET'])
def get_mutual(user_id):
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''
        SELECT DISTINCT l1.to_user_id 
        FROM likes l1
        JOIN likes l2 ON l1.to_user_id = l2.from_user_id AND l1.from_user_id = l2.to_user_id
        WHERE l1.from_user_id = ?
    ''', (user_id,))
    
    mutual_ids = [row['to_user_id'] for row in c.fetchall()]
    users = []
    
    for uid in mutual_ids:
        c.execute('SELECT * FROM users WHERE id = ?', (uid,))
        user = c.fetchone()
        if user:
            u = dict(user)
            u.pop('password', None)
            users.append(u)
    
    conn.close()
    return jsonify({'users': users})

# ========== ПОЛУЧИТЬ ПОЛЬЗОВАТЕЛЯ ==========
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    
    if user:
        u = dict(user)
        u.pop('password', None)
        return jsonify({'user': u})
    return jsonify({'error': 'Not found'}), 404

# ========== СООБЩЕНИЯ ==========
@app.route('/api/messages', methods=['POST'])
def send_message():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO messages (from_user_id, to_user_id, text) VALUES (?,?,?)',
             (data['from_user_id'], data['to_user_id'], data['text']))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/messages/<int:user1>/<int:user2>', methods=['GET'])
def get_messages(user1, user2):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT * FROM messages 
        WHERE (from_user_id = ? AND to_user_id = ?) 
        OR (from_user_id = ? AND to_user_id = ?)
        ORDER BY created_at ASC
    ''', (user1, user2, user2, user1))
    messages = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify({'messages': messages})

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print('=' * 50)
    print('🚀 СЕРВЕР ЗАПУСКАЕТСЯ...')
    print('📡 http://localhost:5000')
    print('🔑 Тестовые пароли: 123')
    print('👥 Пользователи: Анна, Мария, Дмитрий, Алексей')
    print('=' * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)