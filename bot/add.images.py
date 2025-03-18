import sqlite3

# Подключение к существующей базе данных
conn = sqlite3.connect('users.db')  # Убедитесь, что файл users.db существует
cursor = conn.cursor()

# Создание таблицы images (если её ещё нет)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image BLOB,
        name TEXT
    )
''')

# Функция для добавления картинки в базу данных
def add_image_to_db(image_path, image_name):
    # Открываем файл картинки в бинарном режиме
    with open(image_path, "rb") as f:
        image_data = f.read()  # Читаем содержимое файла как байты (BLOB)
    
    # Вставляем данные в таблицу (картинка + её имя)
    cursor.execute("INSERT INTO images (image, name) VALUES (?, ?)", (image_data, image_name))
    conn.commit()
    print(f"Картинка {image_path} с именем '{image_name}' успешно добавлена в базу данных.")

# Добавляем картинки в базу данных
# Замените пути на реальные пути к вашим картинкам и укажите их имена
add_image_to_db(r"D:\imgs\7.jpg", "jaydes")
add_image_to_db(r"D:\imgs\8.jpg", "tayler")

# Закрываем соединение с базой данных
conn.close()
