from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ConversationHandler
)
from database import init_db
from handlers import (
    start,
    handle_text,
    add_card_start,
    add_card_image,
    add_card_name,
    admin_panel,
    get_map,
    show_my_cards,
    handle_delete_card,
    handle_delete_card_id,
    handle_back_button,
    add_card_rarity,
    add_card_style,
    add_card_pname,
    get_current_time,
    add_attempts_start,
    add_attempts_username,
    add_attempts_count,
    handle_player_button,  # Новый обработчик для кнопки "Игрок"
    handle_add_card_to_player_callback,  # Обработчик инлайн-кнопки "Добавить карту игроку"
    add_card_username,  # Обработчик ввода имени пользователя
    add_card_id,
    error_handler  # Обработчик ошибок
)
from pagination import handle_pagination_buttons
from states import (
    WAITING_FOR_IMAGE,
    WAITING_FOR_NAME,
    WAITING_FOR_RARITY,
    WAITING_FOR_STYLE,
    WAITING_FOR_PNAME,
    WAITING_FOR_USERNAME,
    WAITING_FOR_ATTEMPTS,
    WAITING_FOR_CARD_ID  # Новое состояние для ID карты
)
from config import ADMIN_IDS

def main() -> None:
    TOKEN = "7762490778:AAGnDmm8BSCS_vkJg7BRRMK5R5tTtn-keVM"

    application = Application.builder().token(TOKEN).build()

    # ConversationHandler для добавления карты игроку
    conv_handler_add_card_to_player = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_add_card_to_player_callback, pattern="^add_card_to_player$")],
        states={
            WAITING_FOR_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_card_username)],
            WAITING_FOR_CARD_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_card_id)]
        },
        fallbacks=[]
    )

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(conv_handler_add_card_to_player)

    # Обработчик для кнопки "Игрок"
    application.add_handler(MessageHandler(filters.Regex("^Игрок$"), handle_player_button))

    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(handle_pagination_buttons))

    # Специфические обработчики текстовых сообщений
    application.add_handler(MessageHandler(filters.Regex("^Получить карту$"), get_map))
    application.add_handler(MessageHandler(filters.Regex("^Мои карты$"), show_my_cards))
    application.add_handler(MessageHandler(filters.Regex("^Удалить карту$"), handle_delete_card))
    application.add_handler(MessageHandler(filters.Regex("^Назад$"), handle_back_button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_delete_card_id))  # Обработчик ID карты

    # Общий обработчик текстовых сообщений должен быть последним
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)

    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
