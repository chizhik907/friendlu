import sqlite3
import hashlib
from datetime import datetime

class Database:
    def __init__(self, db_path='dating.db'):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Получить соединение с БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Чтобы возвращать словари
        return conn

    def init_db(self):
        """Создать все таблицы при первом запуске"""
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

        # Добавляем тестовых пользователей, если таблица пуста
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            self._create_test_users(cursor)

        conn.commit()
        conn.close()
        print('✅ База данных инициализирована')

    def _create_test_users(self, cursor):
        """Создать тестовых пользователей"""
        test_users = [
            ('Анна', '123', 'female', 24, 'Москва', 'Люблю кофе и уютные вечера', 'https://i.pravatar.cc/400?img=1'),
            ('Екатерина', '123', 'female', 27, 'СПб', 'Ищу серьезные отношения', 'https://i.pravatar.cc/400?img=5'),
            ('Мария', '123', 'female', 22, 'Казань', 'Спорт и путешествия', 'https://i.pravatar.cc/400?img=10'),
            ('Ольга', '123', 'female', 29, 'Екатеринбург', 'Люблю готовить и гулять', 'https://i.pravatar.cc/400?img=25'),
            ('Дмитрий', '123', 'male', 26, 'Москва', 'Программист, ищу девушку', 'https://i.pravatar.cc/400?img=11'),
            ('Алексей', '123', 'male', 30, 'Сочи', 'Активный отдых и море', 'https://i.pravatar.cc/400?img=12'),
            ('Иван', '123', 'male', 25, 'Новосибирск', 'Спортсмен, добрый', 'https://i.pravatar.cc/400?img=20'),
            ('Сергей', '123', 'male', 32, 'Краснодар', 'В поиске второй половинки', 'https://i.pravatar.cc/400?img=33'),
        ]

        for username, password, gender, age, city, bio, photo in test_users:
            hashed = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (username, password, gender, age, city, bio, photo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, hashed, gender, age, city, bio, photo))

        print('👥 Добавлено 8 тестовых пользователей')

    # ========== МЕТОДЫ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ ==========

    def create_user(self, username, password, gender, age, city, bio=None, photo=None):
        """Создать нового пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, password, gender, age, city, bio, photo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, hashed_password, gender, age, city, bio, photo))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return self.get_user(user_id)
        except sqlite3.IntegrityError:
            conn.close()
            return None

    def get_user(self, user_id):
        """Получить пользователя по ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    def get_user_by_username(self, username):
        """Получить пользователя по имени"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    def update_user(self, user_id, data):
        """Обновить данные пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        fields = []
        values = []
        
        allowed_fields = ['city', 'age', 'bio', 'photo']
        for key, value in data.items():
            if key in allowed_fields and value is not None:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            conn.close()
            return self.get_user(user_id)
        
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        return self.get_user(user_id)

    # ========== МЕТОДЫ ДЛЯ РАБОТЫ С ЛАЙКАМИ ==========

    def add_like(self, from_user_id, to_user_id):
        """Добавить лайк"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO likes (from_user_id, to_user_id)
                VALUES (?, ?)
            ''', (from_user_id, to_user_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

    def get_like(self, from_user_id, to_user_id):
        """Проверить, есть ли лайк"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM likes 
            WHERE from_user_id = ? AND to_user_id = ?
        ''', (from_user_id, to_user_id))
        like = cursor.fetchone()
        conn.close()
        return dict(like) if like else None

    def get_liked_users(self, user_id):
        """Получить ID всех, кого лайкнул пользователь"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT to_user_id FROM likes WHERE from_user_id = ?', (user_id,))
        likes = cursor.fetchall()
        conn.close()
        return [row['to_user_id'] for row in likes]

    def get_mutual_likes(self, user_id):
        """Получить ID всех, с кем есть взаимная симпатия"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT l1.to_user_id as mutual_id
            FROM likes l1
            INNER JOIN likes l2 ON l1.to_user_id = l2.from_user_id AND l1.from_user_id = l2.to_user_id
            WHERE l1.from_user_id = ?
        ''', (user_id,))
        
        mutual = cursor.fetchall()
        conn.close()
        return [row['mutual_id'] for row in mutual]

    # ========== МЕТОДЫ ДЛЯ РАБОТЫ С СООБЩЕНИЯМИ ==========

    def send_message(self, from_user_id, to_user_id, text):
        """Отправить сообщение"""
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
        """Получить сообщение по ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM messages WHERE id = ?', (message_id,))
        message = cursor.fetchone()
        conn.close()
        return dict(message) if message else None

    def get_messages(self, user1_id, user2_id):
        """Получить историю переписки между двумя пользователями"""
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
        return [dict(msg) for msg in messages]

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
        """Пометить сообщения как прочитанные"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE messages SET is_read = 1
            WHERE from_user_id = ? AND to_user_id = ?
        ''', (from_user_id, user_id))
        conn.commit()
        conn.close()

    # ========== МЕТОДЫ ДЛЯ ПОИСКА ==========

    def get_available_users(self, user_id, target_gender):
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
        params = [user_id, target_gender]
        
        if liked_ids:
            placeholders = ','.join(['?'] * len(liked_ids))
            query += f' AND id NOT IN ({placeholders})'
            params.extend(liked_ids)
        
        cursor.execute(query, params)
        users = cursor.fetchall()
        conn.close()
        
        # Убираем пароли
        result = []
        for user in users:
            u = dict(user)
            u.pop('password', None)
            result.append(u)
        
        return result

    # ========== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ==========

    def get_user_count(self):
        """Получить общее количество пользователей"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def delete_user(self, user_id):
        """Удалить пользователя (для тестирования)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        cursor.execute('DELETE FROM likes WHERE from_user_id = ? OR to_user_id = ?', (user_id, user_id))
        cursor.execute('DELETE FROM messages WHERE from_user_id = ? OR to_user_id = ?', (user_id, user_id))
        conn.commit()
        conn.close()