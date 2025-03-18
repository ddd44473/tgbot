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
    handle_back_button,  # Импортируем новую функцию
    add_card_rarity,  # Добавляем новую функцию для обработки редкости
    add_card_style,
    add_card_pname,
    get_current_time
)
from pagination import handle_pagination_buttons
from states import WAITING_FOR_IMAGE, WAITING_FOR_NAME, WAITING_FOR_RARITY, WAITING_FOR_STYLE, WAITING_FOR_PNAME  # Добавляем новое состояние
from config import ADMIN_IDS

def main() -> None:
    # Вставьте сюда ваш токен
    TOKEN = "7762490778:AAGnDmm8BSCS_vkJg7BRRMK5R5tTtn-keVM"

    # Инициализация базы данных
    init_db()

    # Создаем приложение и передаем токен
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Добавить карту$"), add_card_start)],
        states={
            WAITING_FOR_IMAGE: [MessageHandler(filters.PHOTO, add_card_image)],
            WAITING_FOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_card_name)],
            WAITING_FOR_PNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_card_pname)],
            WAITING_FOR_STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_card_style)],
            WAITING_FOR_RARITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_card_rarity)]  # Новое состояние
        },
        fallbacks=[]
    )

    # Добавляем обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(conv_handler)  # ConversationHandler
    application.add_handler(CallbackQueryHandler(handle_pagination_buttons))

    # Специфические обработчики текстовых сообщений
    application.add_handler(MessageHandler(filters.Regex("^Получить карту$"), get_map))
    application.add_handler(MessageHandler(filters.Regex("^Мои карты$"), show_my_cards))
    application.add_handler(MessageHandler(filters.Regex("^Удалить карту$"), handle_delete_card))
    application.add_handler(MessageHandler(filters.Regex("^Назад$"), handle_back_button))  # Обработчик кнопки "Назад"
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_delete_card_id))  # Обработчик ID карты

    # Общий обработчик текстовых сообщений должен быть последним
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
