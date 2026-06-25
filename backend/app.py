# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import Database  # <-- Используем database.py

app = Flask(__name__)
CORS(app)

# ========== ИНИЦИАЛИЗАЦИЯ БАЗЫ ==========
db = Database()  # <-- Создаёт БД в backend/instance/

# ========== ГЛАВНАЯ ==========
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'ok',
        'message': '❤️ Сервер знакомств работает!',
        'db_path': db.db_path,
        'users_count': db.get_user_count(),
        'test_users': ['Анна', 'Мария', 'Дмитрий', 'Алексей', 'Екатерина', 'Ольга', 'Иван', 'Сергей'],
        'test_password': '123'
    })

# ========== РЕГИСТРАЦИЯ ==========
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    print('📝 Регистрация:', data['username'])
    
    user = db.create_user(
        username=data['username'],
        password=data['password'],
        gender=data['gender'],
        age=int(data['age']),
        city=data['city'],
        bio=data.get('bio', 'Люблю знакомиться!'),
        photo=data.get('photo')
    )
    
    if not user:
        return jsonify({'error': 'Пользователь уже существует'}), 400
    
    user.pop('password', None)
    return jsonify({'success': True, 'user': user}), 201

# ========== ВХОД ==========
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    print('🔑 Вход:', data['username'])
    
    user = db.get_user_by_username(data['username'])
    
    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 401
    
    if user['password'] == data['password']:
        user.pop('password', None)
        return jsonify({'success': True, 'user': user}), 200
    else:
        return jsonify({'error': 'Неверный пароль'}), 401

# ========== ДОСТУПНЫЕ АНКЕТЫ ==========
@app.route('/api/users/<int:user_id>/available', methods=['GET'])
def get_available(user_id):
    print(f'📋 Запрос анкет для пользователя {user_id}')
    
    user = db.get_user(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    target = 'female' if user['gender'] == 'male' else 'male'
    users = db.get_available_users(user_id, target)
    
    return jsonify({'users': users})

# ========== ЛАЙК ==========
@app.route('/api/likes', methods=['POST'])
def add_like():
    data = request.json
    
    if not data.get('from_user_id') or not data.get('to_user_id'):
        return jsonify({'error': 'Не указаны пользователи'}), 400
    
    success = db.add_like(data['from_user_id'], data['to_user_id'])
    
    if not success:
        return jsonify({'error': 'Вы уже лайкнули этого пользователя'}), 400
    
    # Проверяем взаимность
    mutual = db.get_like(data['to_user_id'], data['from_user_id'])
    is_mutual = mutual is not None
    
    return jsonify({
        'success': True,
        'is_mutual': is_mutual
    })

# ========== ВЗАИМНЫЕ СИМПАТИИ ==========
@app.route('/api/users/<int:user_id>/mutual', methods=['GET'])
def get_mutual(user_id):
    print(f'💞 Запрос взаимных симпатий для {user_id}')
    
    mutual_ids = db.get_mutual_likes(user_id)
    users = []
    
    for uid in mutual_ids:
        user = db.get_user(uid)
        if user:
            user.pop('password', None)
            users.append(user)
    
    return jsonify({'users': users})

# ========== ПОЛУЧИТЬ ПОЛЬЗОВАТЕЛЯ ==========
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.get_user(user_id)
    if not user:
        return jsonify({'error': 'Not found'}), 404
    
    user.pop('password', None)
    return jsonify({'user': user})

# ========== СООБЩЕНИЯ ==========
@app.route('/api/messages', methods=['POST'])
def send_message():
    data = request.json
    message = db.send_message(
        data['from_user_id'],
        data['to_user_id'],
        data['text']
    )
    return jsonify({'message': message})

@app.route('/api/messages/<int:user1>/<int:user2>', methods=['GET'])
def get_messages(user1, user2):
    messages = db.get_messages(user1, user2)
    return jsonify({'messages': messages})

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print('=' * 50)
    print('🚀 СЕРВЕР ЗАПУСКАЕТСЯ...')
    print('📡 http://localhost:5000')
    print(f'📂 База данных: {db.db_path}')
    print('🔑 Тестовые пароли: 123')
    print('=' * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)