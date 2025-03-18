from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.ext import ContextTypes  # Импортируем ContextTypes
from state_manager import get_current_index, set_current_index
from database import get_user_images, update_user_points, get_user_points

# Функция для отправки карты с кнопками
async def send_card_with_pagination(update, context, user_id, images):
    current_index = get_current_index(user_id)

    # Корректируем индекс, если он выходит за границы
    if current_index < 0:
        current_index = 0
    elif current_index >= len(images):
        current_index = len(images) - 1

    set_current_index(user_id, current_index)

    # Получаем текущую карту, её название и редкость
    image_data, image_name, rarity, style, pname = images[current_index]

    # Создаем кнопки пагинации
    keyboard = [
        [
            InlineKeyboardButton("⬅️ Назад", callback_data="prev"),
            InlineKeyboardButton("Вперёд ➡️", callback_data="next")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    current_points = get_user_points(user_id)

    # Формируем текст подписи
    name_caption = f"<b>{pname}</b> - {image_name}\n" if image_name else "Название отсутствует"
    #rarity_caption = f"<b>{rarity} Pts</b>\n"
    style_caption = f"Rarity - <b>{style}</b>\n"
    points_caption = f"Points in this season: <b>{current_points} pts</b>\n"
    pagination_caption = f"Карта {current_index + 1} из {len(images)}"

    caption = f"\n{name_caption}\n{style_caption}\n{points_caption}\n{pagination_caption}"

    # Отправляем карту с её подписью
    await update.message.reply_photo(
        photo=image_data,
        caption=caption,
        parse_mode="HTML",  # Указываем режим форматирования
        reply_markup=reply_markup
    )

# Обработчик inline-кнопок
async def handle_pagination_buttons(update, context):
    query = update.callback_query
    await query.answer()

    action = query.data
    user_id = query.from_user.id

    # Получаем все карты пользователя
    images = get_user_images(user_id)
    if not images:
        await query.edit_message_text("У вас пока нет сохранённых карт.")
        return

    # Обновляем индекс в зависимости от действия
    current_index = get_current_index(user_id)
    if action == "prev":
        current_index -= 1
    elif action == "next":
        current_index += 1

    # Проверяем границы индекса
    if current_index < 0:
        current_index = 0
    elif current_index >= len(images):
        current_index = len(images) - 1

    set_current_index(user_id, current_index)

    # Получаем новую карту, её название и редкость
    image_data, image_name, rarity, style, pname = images[current_index]

    current_points = get_user_points(user_id)

    # Формируем текст подписи
    name_caption = f"<b>{pname}</b> - {image_name}\n" if image_name else "Название отсутствует"
    #rarity_caption = f"<b>{rarity} Pts</b>\n"
    style_caption = f"Rarity - <b>{style}</b>\n"
    points_caption = f"Points in this season: <b>{current_points} pts</b>\n"
    pagination_caption = f"Карта {current_index + 1} из {len(images)}"

    caption = f"\n{name_caption}\n{style_caption}\n{points_caption}\n{pagination_caption}"

    # Обновляем медиа и подпись
    await query.message.edit_media(
        media=InputMediaPhoto(media=image_data, caption=caption, parse_mode="HTML"),
        reply_markup=query.message.reply_markup
    )
