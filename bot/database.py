import sqlite3

import random

# Словарь с весами для стилей
STYLE_WEIGHTS = {
    "Actor": 99,
    "Director": 1,
}



# Подключение к базе данных SQLite
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Создаем таблицу, если она еще не существует
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image BLOB
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            image_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (image_id) REFERENCES images(id)
        )
    ''')
    conn.commit()
    conn.close()


# Функция для добавления пользователя в базу данных
def add_user_to_db(user_id: int, username: str, first_name: str):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Проверяем, существует ли пользователь в базе данных
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    if not cursor.fetchone():  # Если пользователя нет, добавляем его
        cursor.execute('INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?)', (user_id, username, first_name))
        conn.commit()
    conn.close()

def get_random_image():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()

        # Получаем все доступные стили и их веса
        styles = list(STYLE_WEIGHTS.keys())
        weights = list(STYLE_WEIGHTS.values())

        # Выбираем случайный стиль с учетом весов
        selected_style = random.choices(styles, weights=weights, k=1)[0]

        # Получаем случайную карту выбранного стиля
        cursor.execute('''
            SELECT id, image, name, rarity, style, pname
            FROM images
            WHERE style = ?
            ORDER BY RANDOM()
            LIMIT 1
        ''', (selected_style,))
        result = cursor.fetchone()

    return result


# Функция для добавления карты в базу данных пользователя
def add_image_to_user(user_id, image_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Добавляем запись о связи в таблицу user_images
    cursor.execute('''
        INSERT INTO user_images (user_id, image_id)
        VALUES (?, ?)
    ''', (user_id, image_id))

    conn.commit()
    conn.close()


# Функция для получения всех карт пользователя
def get_user_images(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT i.image, i.name, i.rarity, i.style, i.pname
        FROM images i
        JOIN user_images ui ON i.id = ui.image_id
        WHERE ui.user_id = ?
    ''', (user_id,))
    images = cursor.fetchall()
    conn.close()
    return images

def get_all_images():
    with sqlite3.connect('users.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM images")
        return cursor.fetchall()  # Возвращает список кортежей (id, name)

def delete_image(image_id):
    with sqlite3.connect('users.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        # Удаляем саму картинку
        cursor.execute("DELETE FROM images WHERE id = ?", (image_id,))
        # Удаляем связи с пользователями
        cursor.execute("DELETE FROM user_images WHERE image_id = ?", (image_id,))
        conn.commit()
    print(f"Карта с ID {image_id} успешно удалена.")


def add_image_to_db(image_data, image_name, rarity, style, pname):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO images (image, name, rarity, style, pname)
        VALUES (?, ?, ?, ?, ?)
    ''', (image_data, image_name, rarity, style, pname))
    conn.commit()
    conn.close()


def update_user_points(user_id: int, points_to_add: int):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Увеличиваем количество Points на points_to_add
    cursor.execute('''
        UPDATE users
        SET Points = Points + ?
        WHERE user_id = ?
    ''', (points_to_add, user_id))
    conn.commit()
    conn.close()


def get_user_points(user_id: int) -> int:
    """
    Получает текущее количество Points пользователя.
    :param user_id: ID пользователя.
    :return: Количество Points или 0, если пользователь не найден.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT Points FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

