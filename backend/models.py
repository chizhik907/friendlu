import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self, db_path='dating.db'):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Создание всех таблиц"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                gender TEXT NOT NULL,
                age INTEGER NOT NULL,
                city TEXT NOT NULL,
                bio TEXT,
                photo TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица лайков
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user_id INTEGER NOT NULL,
                to_user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_user_id) REFERENCES users (id),
                FOREIGN KEY (to_user_id) REFERENCES users (id),
                UNIQUE(from_user_id, to_user_id)
            )
        ''')

        # Таблица сообщений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user_id INTEGER NOT NULL,
                to_user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_user_id) REFERENCES users (id),
                FOREIGN KEY (to_user_id) REFERENCES users (id)
            )
        ''')

        # Добавляем тестовых пользователей, если их нет
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            self.create_test_users()

        conn.commit()
        conn.close()

    def create_test_users(self):
        """Создание тестовых пользователей"""
        test_users = [
            ('Анна', 'password123', 'female', 24, 'Москва', 'Люблю кофе и уютные вечера', 'https://i.pravatar.cc/400?img=1'),
            ('Екатерина', 'password123', 'female', 27, 'СПб', 'Ищу серьезные отношения', 'https://i.pravatar.cc/400?img=5'),
            ('Мария', 'password123', 'female', 22, 'Казань', 'Спорт и путешествия', 'https://i.pravatar.cc/400?img=10'),
            ('Ольга', 'password123', 'female', 29, 'Екатеринбург', 'Люблю готовить и гулять', 'https://i.pravatar.cc/400?img=25'),
            ('Дмитрий', 'password123', 'male', 26, 'Москва', 'Программист, ищу девушку', 'https://i.pravatar.cc/400?img=11'),
            ('Алексей', 'password123', 'male', 30, 'Сочи', 'Активный отдых и море', 'https://i.pravatar.cc/400?img=12'),
            ('Иван', 'password123', 'male', 25, 'Новосибирск', 'Спортсмен, добрый', 'https://i.pravatar.cc/400?img=20'),
            ('Сергей', 'password123', 'male', 32, 'Краснодар', 'В поиске второй половинки', 'https://i.pravatar.cc/400?img=33'),
        ]

        conn = self.get_connection()
        cursor = conn.cursor()
        
        for username, password, gender, age, city, bio, photo in test_users:
            cursor.execute('''
                INSERT INTO users (username, password, gender, age, city, bio, photo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, password, gender, age, city, bio, photo))
        
        conn.commit()
        conn.close()

    # ========== ПОЛЬЗОВАТЕЛИ ==========
    
    def create_user(self, username, password, gender, age, city, bio, photo):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (username, password, gender, age, city, bio, photo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, password, gender, age, city, bio, photo))
            conn.commit()
            user_id = cursor.lastrowid
            return self.get_user(user_id)
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    def get_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    def get_user_by_username(self, username):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    def update_user(self, user_id, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        fields = []
        values = []
        
        for key, value in data.items():
            if key in ['city', 'age', 'bio', 'photo']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            return self.get_user(user_id)
        
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        return self.get_user(user_id)

    # ========== ЛАЙКИ ==========
    
    def add_like(self, from_user_id, to_user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO likes (from_user_id, to_user_id)
                VALUES (?, ?)
            ''', (from_user_id, to_user_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def get_like(self, from_user_id, to_user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM likes WHERE from_user_id = ? AND to_user_id = ?
        ''', (from_user_id, to_user_id))
        like = cursor.fetchone()
        conn.close()
        return dict(like) if like else None

    def get_mutual_likes(self, user_id):
        """Найти все взаимные лайки для пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l1.to_user_id as mutual_user_id
            FROM likes l1
            INNER JOIN likes l2 ON l1.to_user_id = l2.from_user_id AND l1.from_user_id = l2.to_user_id
            WHERE l1.from_user_id = ?
        ''', (user_id,))
        mutual = cursor.fetchall()
        conn.close()
        return [dict(m)['mutual_user_id'] for m in mutual]

    def get_liked_users(self, user_id):
        """Получить всех пользователей, которых лайкнул данный пользователь"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT to_user_id FROM likes WHERE from_user_id = ?', (user_id,))
        likes = cursor.fetchall()
        conn.close()
        return [dict(l)['to_user_id'] for l in likes]

    # ========== СООБЩЕНИЯ ==========
    
    def send_message(self, from_user_id, to_user_id, text):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (from_user_id, to_user_id, text)
            VALUES (?, ?, ?)
        ''', (from_user_id, to_user_id, text))
        conn.commit()
        message_id = cursor.lastrowid
        conn.close()
        return self.get_message(message_id)

    def get_message(self, message_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM messages WHERE id = ?', (message_id,))
        message = cursor.fetchone()
        conn.close()
        return dict(message) if message else None

    def get_messages(self, user1_id, user2_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM messages 
            WHERE (from_user_id = ? AND to_user_id = ?)
            OR (from_user_id = ? AND to_user_id = ?)
            ORDER BY created_at ASC
        ''', (user1_id, user2_id, user2_id, user1_id))
        messages = cursor.fetchall()
        conn.close()
        return [dict(m) for m in messages]

    def get_unread_count(self, user_id):
        """Получить количество непрочитанных сообщений"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM messages 
            WHERE to_user_id = ? AND is_read = 0
        ''', (user_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def mark_messages_as_read(self, user_id, from_user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE messages SET is_read = 1
            WHERE from_user_id = ? AND to_user_id = ?
        ''', (from_user_id, user_id))
        conn.commit()
        conn.close()

    # ========== ПОИСК АНКЕТ ==========
    
    def get_available_users(self, user_id, gender_filter):
        """Получить доступные анкеты (противоположный пол + не лайкнутые)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Получаем ID уже лайкнутых
        liked_ids = self.get_liked_users(user_id)
        
        # Формируем запрос
        query = '''
            SELECT * FROM users 
            WHERE id != ? 
            AND gender = ?
        '''
        params = [user_id, gender_filter]
        
        if liked_ids:
            placeholders = ','.join(['?'] * len(liked_ids))
            query += f' AND id NOT IN ({placeholders})'
            params.extend(liked_ids)
        
        cursor.execute(query, params)
        users = cursor.fetchall()
        conn.close()
        return [dict(u) for u in users]