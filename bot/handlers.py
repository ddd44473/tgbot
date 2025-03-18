from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from database import (
    add_user_to_db,
    get_random_image,
    add_image_to_user,
    get_user_images,
    add_image_to_db,
    delete_image,
    get_all_images,
    update_user_points,
    get_user_points
)
from pagination import send_card_with_pagination
from states import WAITING_FOR_IMAGE, WAITING_FOR_NAME, WAITING_FOR_RARITY, WAITING_FOR_STYLE, WAITING_FOR_PNAME
from config import ADMIN_IDS

import time

import sqlite3

# Начало процесса добавления карты
async def add_card_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Проверяем, является ли пользователь администратором
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return ConversationHandler.END

    # Если пользователь администратор
    if update.message.text == "Добавить карту":
        await update.message.reply_text("Пожалуйста, отправьте картинку.")
        return WAITING_FOR_IMAGE

# Получение картинки
async def add_card_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверяем, что сообщение содержит фотографию
    if update.message.photo:
        # Получаем файл фотографии
        photo_file = await update.message.photo[-1].get_file()
        # Сохраняем данные изображения в user_data
        context.user_data['image_data'] = await photo_file.download_as_bytearray()
        # Запрашиваем название карты
        await update.message.reply_text("Теперь отправьте название для этой карты.")
        return WAITING_FOR_NAME  # Переходим к следующему состоянию
    else:
        # Если сообщение не содержит фотографию, просим отправить картинку снова
        await update.message.reply_text("Пожалуйста, отправьте картинку.")
        return WAITING_FOR_IMAGE  # Оставляем бота в состоянии ожидания картинки

# Получение названия
async def add_card_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    image_name = update.message.text.strip()
    if not image_name:
        await update.message.reply_text("Пожалуйста, отправьте корректное название карты.")
        return WAITING_FOR_NAME

    context.user_data['image_name'] = image_name  # Сохраняем название в user_data
    await update.message.reply_text("Теперь отправьте имя персонажа, связанного с этой картой.")
    return WAITING_FOR_PNAME  # Переходим к следующему состоянию

# Получение имени персонажа
async def add_card_pname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pname = update.message.text.strip()  # Убираем лишние пробелы
    if not pname:
        await update.message.reply_text("Пожалуйста, отправьте корректное имя персонажа.")
        return WAITING_FOR_PNAME  # Оставляем бота в текущем состоянии

    context.user_data['pname'] = pname  # Сохраняем имя персонажа
    await update.message.reply_text("Теперь отправьте стиль карты (строка).")
    return WAITING_FOR_STYLE  # Переходим к следующему состоянию


# Получение стиля
async def add_card_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    style = update.message.text.strip()  # Убираем лишние пробелы
    if not style:
        await update.message.reply_text("Пожалуйста, отправьте корректный стиль.")
        return WAITING_FOR_STYLE  # Оставляем бота в текущем состоянии

    context.user_data['style'] = style  # Сохраняем стиль
    await update.message.reply_text("Теперь отправьте редкость карты (число).")
    return WAITING_FOR_RARITY  # Переходим к следующему состоянию


# Получение редкости
async def add_card_rarity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        rarity = int(update.message.text)  # Преобразуем текст в число
    except ValueError:
        await update.message.reply_text("Пожалуйста, отправьте корректное число для редкости.")
        return WAITING_FOR_RARITY  # Оставляем бота в состоянии ожидания редкости

    # Получаем данные из user_data
    image_data = context.user_data.get('image_data')
    image_name = context.user_data.get('image_name')
    style = context.user_data.get('style')
    pname = context.user_data.get('pname')

    if image_data and image_name and style:
        # Добавляем карту в базу данных
        add_image_to_db(image_data, image_name, rarity, style, pname)
        await update.message.reply_text("Карта успешно добавлена!")
    else:
        await update.message.reply_text("Произошла ошибка. Попробуйте снова.")

    context.user_data.clear()  # Очищаем временные данные
    return ConversationHandler.END  # Завершаем диалог


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Проверяем, является ли пользователь администратором
    if user_id not in ADMIN_IDS:
        return  # Игнорируем запрос

    keyboard = [
        ["Добавить карту", "Удалить карту"],
        ["Статистика", "Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Вы вошли в панель администратора. Выберите действие:",
        reply_markup=reply_markup
    )

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    first_name = update.message.from_user.first_name
    add_user_to_db(user_id, username, first_name)

    if user_id in ADMIN_IDS:
        keyboard = [
            ["Получить карту", "Мои карты"],
            ["О боте"]
        ]
    else:
        keyboard = [
            ["Получить карту", "Мои карты"],
            ["О боте"]
        ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"Привет, {first_name}! Я бот. Выберите действие:",
        reply_markup=reply_markup
    )


# Функция для получения текущего времени в секундах
def get_current_time():
    return int(time.time())


# Обработчик кнопки "Получить карту"
async def get_map(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Получить карту":
        result = get_random_image()
        if not result:
            await update.message.reply_text("Картинки не найдены. Попробуйте позже.")
            return
        image_id, image_data, image_name, rarity, style, pname = result  # Добавляем редкость
        user_id = update.message.from_user.id

        # Получаем время последнего получения карты
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT last_card_time FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        last_card_time = result[0] if result else 0

        # Текущее время
        current_time = get_current_time()

        # Проверяем, прошло ли 4 часа (14400 секунд)
        if current_time - last_card_time < 14400:
            remaining_seconds = 14400 - (current_time - last_card_time)
            remaining_hours = remaining_seconds // 3600  # Преобразуем секунды в часы
            remaining_minutes = (remaining_seconds % 3600) // 60  # Оставшиеся минуты
            await update.message.reply_text(
                f"Вы сможете получить новую карту через {remaining_hours} часов и {remaining_minutes} минут."
            )
            return

        # Если прошло 3 минуты, обновляем время и выдаем карту
        cursor.execute('''
            UPDATE users
            SET last_card_time = ?
            WHERE user_id = ?
        ''', (current_time, user_id))
        conn.commit()
        conn.close()

        # Обновляем количество Points пользователя
        update_user_points(user_id, rarity)

        current_points = get_user_points(user_id)
        
        # Формируем подпись с HTML-форматированием
        caption = (
            f"<b>{pname}</b> - {image_name}\n"
            f"\n<b>+ {rarity}</b> points\n"
            f"\nRarity: <b>{style}</b>\n"
            f"\nPoints: <b>{current_points} pts</b>"
            #f"Points"
        ) if image_name else (
            f"Редкость: <b>{rarity}</b>\n"
            f"Стиль: <b>{style}</b>"
        )
        
        # Отправляем изображение с подписью
        await context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=image_data,
            caption=caption,
            parse_mode="HTML"
        )
        add_image_to_user(user_id, image_id)

# Обработчик кнопки "Мои карты"
async def show_my_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Мои карты":
        user_id = update.message.from_user.id
        images = get_user_images(user_id)

        if not images:
            await update.message.reply_text("У вас пока нет сохранённых карт.")
            return

        await send_card_with_pagination(update, context, user_id, images)

async def handle_delete_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Проверяем, является ли пользователь администратором
    if user_id not in ADMIN_IDS:
        return  # Игнорируем запрос

    # Получаем список всех карт
    images = get_all_images()

    if not images:
        await update.message.reply_text("Нет доступных карт для удаления.")
        return

    # Формируем сообщение со списком карт
    message = "Выберите ID карты для удаления:\n"
    for image_id, image_name in images:
        message += f"{image_id}: {image_name or 'Без названия'}\n"

    # Сохраняем состояние для ожидания выбора ID
    context.user_data['delete_mode'] = True
    await update.message.reply_text(message)

async def handle_delete_card_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Функция handle_delete_card_id вызвана")  # Отладочная информация

    if not context.user_data.get('delete_mode'):
        return  # Если не в режиме удаления, игнорируем

    try:
        # Получаем ID карты из сообщения
        image_id = int(update.message.text)

        # Удаляем карту
        delete_image(image_id)
        await update.message.reply_text(f"Карта с ID {image_id} успешно удалена.")

    except ValueError:
        await update.message.reply_text("Пожалуйста, отправьте корректный ID карты.")

    # Очищаем флаг delete_mode
    context.user_data.pop('delete_mode', None)

async def handle_back_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    # Очищаем все флаги в context.user_data
    context.user_data.clear()
    # Клавиатура обычного пользователя (панель игрока)
    keyboard = [
        ["Получить карту", "Мои карты"],
        ["О боте"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Вы вернулись в главное меню.",
        reply_markup=reply_markup
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Получено сообщение в handle_text: {update.message.text}")  # Отладочная информация

    user_id = update.message.from_user.id
    username = update.message.from_user.username
    first_name = update.message.from_user.first_name
    add_user_to_db(user_id, username, first_name)

    if update.message.text == "Назад":
        # Очищаем все флаги в context.user_data
        context.user_data.clear()

        # Клавиатура обычного пользователя (панель игрока)
        keyboard = [
            ["Получить карту", "Мои карты"],
            ["О боте"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            f"Вы вернулись в главное меню, {first_name}.",
            reply_markup=reply_markup
        )
        return

    # Обработка других текстовых сообщений
    await update.message.reply_text("Я не понимаю эту команду. Пожалуйста, используйте кнопки меню.")
