import sqlite3
import hashlib
import os
from datetime import datetime

class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            # Берём папку, где лежит database.py
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # Создаём папку instance рядом с database.py
            instance_dir = os.path.join(base_dir, 'instance')
            if not os.path.exists(instance_dir):
                os.makedirs(instance_dir)
                print(f'📁 Создана папка: {instance_dir}')
            db_path = os.path.join(instance_dir, 'dating.db')
        self.db_path = db_path
        print(f'📂 База данных: {self.db_path}')
        self.init_db()

    def get_connection(self):
        """Получить соединение с БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
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
        print(f'✅ База данных инициализирована: {self.db_path}')

    def _create_test_users(self, cursor):
        """Создать тестовых пользователей"""
        test_users = [
            ('Анна', '123', 'female', 24, 'Москва', 'Люблю кофе и уютные вечера', 'https://i.pinimg.com/736x/be/3a/2d/be3a2dddce76085b2d55eaaeaa827c12.jpg'),
            ('Екатерина', '123', 'female', 27, 'СПб', 'Ищу серьезные отношения', 'https://i.pinimg.com/736x/a0/54/4e/a0544e33c200b3a2752e75520dbe794a.jpg'),
            ('Мария', '123', 'female', 22, 'Казань', 'Спорт и путешествия', 'https://i.pinimg.com/736x/a0/54/4e/a0544e33c200b3a2752e75520dbe794a.jpg'),
            ('Ольга', '123', 'female', 44, 'Екатеринбург', 'Люблю готовить и гулять', 'https://i.pinimg.com/736x/d1/ea/75/d1ea753267e31672339ad8a1cdb28baf.jpg'),
            ('Дмитрий', '123', 'male', 26, 'Москва', 'Программист, ищу девушку', 'https://i.pinimg.com/736x/d0/cc/b1/d0ccb1fceba44f15054157ce2664b3d7.jpg'),
            ('Алексей', '123', 'male', 30, 'Сочи', 'Активный отдых и море', 'https://i.pinimg.com/736x/65/5c/45/655c450963bafebbaaa4ed34ba0fbda0.jpg'),
            ('Иван', '123', 'male', 25, 'Новосибирск', 'Спортсмен, добрый', 'https://i.pinimg.com/736x/93/12/86/9312869848ff8bf846afc42b1e8711d0.jpg'),
            ('Сергей', '123', 'male', 32, 'Краснодар', 'В поиске второй половинки', 'https://i.pinimg.com/736x/f2/7a/6f/f27a6fc79c0ae430be96990864de7e13.jpg'),
            ('Саня', '123', 'male', 18, 'Благовещенск', 'В поиске второго рональдо', 'https://i.pinimg.com/736x/ee/e3/e6/eee3e683f79c1ab8a230e13c850ffbe8.jpg'),
            ('Дарья', '123', 'female', 11, 'Москва', 'Люблю уютные вечера', 'https://i.pinimg.com/736x/b1/66/74/b166743768f2edd46e756b630f7ffb4a.jpg'),
            ('Варвара', '123', 'female', 15, 'СПб', 'Ищу серьезные отношения', 'https://i.pinimg.com/736x/a0/54/4e/a0544e33c200b3a2752e75520dbe794a.jpg'),
            ('Владислава', '123', 'female', 32, 'Москва', 'Люблю кофе и уютные вечера', 'https://i.pinimg.com/736x/47/d6/95/47d69577f0dd61162ec7526f2ead84dc.jpg '),
            ('Елизавета', '123', 'female', 27, 'СПб', 'Ищу серьезные отношения', 'https://i.pinimg.com/736x/a0/54/4e/a0544e33c200b3a2752e75520dbe794a.jpg'),
            ('Кристина', '123', 'female', 22, 'Казань', 'Спорт и путешествия', 'https://i.pinimg.com/736x/37/02/e9/3702e9686649a7d1b5c731a1b8cc237b.jpg'),
            ('Эвелина', '123', 'female', 28, 'Екатеринбург', 'Люблю готовить и гулять', 'https://i.pinimg.com/736x/49/ed/99/49ed99b1830be71cc6e6b78fb59589f8.jpg'),
            ('Илья', '123', 'male', 29, 'Москва', 'Программист, ищу девушку', 'https://i.pinimg.com/736x/2f/a8/e9/2fa8e91fa5c0a46a57b765dc923054f5.jpg'),
            ('Ярослав', '123', 'male', 33, 'Сочи', 'Активный отдых и море', 'https://i.pinimg.com/736x/80/a6/d3/80a6d39aaf68de0d0a1aabf1fb2aaf6d.jpg '),
            ('Степа', '123', 'male', 21, 'Новосибирск', 'Спортсмен, добрый', 'https://i.pinimg.com/736x/71/a2/bb/71a2bb8f2c573d77b928d0bd61b7cb2e.jpg '),
            ('Руслан', '123', 'male', 23, 'Краснодар', 'В поиске второй половинки', 'https://i.pinimg.com/736x/78/2a/99/782a99e836e19c53bb92e8d4d0e96daf.jpg'),
            ('Арсений', '123', 'male', 5, 'Благовещенск', 'В поиске второго хакера', 'https://i.pinimg.com/736x/f5/d0/25/f5d02515210afb38f4dff6c25732044f.jpg'),
            ('Есения', '123', 'female', 13, 'Москва', 'Люблю уютные вечера', 'https://i.pinimg.com/736x/a0/54/4e/a0544e33c200b3a2752e75520dbe794a.jpg'),
            ('Соня', '123', 'female', 22, 'СПб', 'Ищу серьезные отношения', 'https://i.pinimg.com/736x/5d/be/40/5dbe40a84a1a4809de1dbeefe1bc2d35.jpg'),
        ]

        for username, password, gender, age, city, bio, photo in test_users:
            cursor.execute('''
                INSERT INTO users (username, password, gender, age, city, bio, photo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, password, gender, age, city, bio, photo))

        print('👥 Добавлено 8 тестовых пользователей (пароль: 123)')

    # ========== МЕТОДЫ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ ==========

    def create_user(self, username, password, gender, age, city, bio=None, photo=None):
        """Создать нового пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, password, gender, age, city, bio, photo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, password, gender, age, city, bio, photo))
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