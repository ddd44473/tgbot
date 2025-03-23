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
    handle_user_button,
    handle_username_input,
    handle_add_attempts_start,
    add_attempts_count,
    add_attempts_username,  # Добавляем новую функцию,
    handle_view_cards
)
from pagination import handle_pagination_buttons
from states import (
    WAITING_FOR_IMAGE,
    WAITING_FOR_NAME,
    WAITING_FOR_PNAME,
    WAITING_FOR_RARITY,
    WAITING_FOR_STYLE,
    WAITING_FOR_USERNAME,
    WAITING_FOR_ACTION,
    WAITING_FOR_ATTEMPTS
)
from config import ADMIN_IDS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main() -> None:
    # Вставьте сюда ваш токен
    TOKEN = "7762490778:AAGnDmm8BSCS_vkJg7BRRMK5R5tTtn-keVM"

    # Инициализация базы данных
    init_db()

    # Создаем приложение и передаем токен
    application = Application.builder().token(TOKEN).build()

    # ConversationHandler для добавления карт
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Добавить карту$"), add_card_start)],
        states={
            WAITING_FOR_IMAGE: [MessageHandler(filters.PHOTO, add_card_image)],
            WAITING_FOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_card_name)],
            WAITING_FOR_PNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_card_pname)],
            WAITING_FOR_STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_card_style)],
            WAITING_FOR_RARITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_card_rarity)]
        },
        fallbacks=[]
    )

    # ConversationHandler для работы с пользователем (кнопка "Пользователь")
    conv_handler_user = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Пользователь$"), handle_user_button)],
        states={
            WAITING_FOR_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_attempts_username)],  # Переход к выбору действия
            WAITING_FOR_ACTION: [
                MessageHandler(filters.Regex("^Выдать попытки$"), handle_add_attempts_start),  # Выбор действия "Выдать попытки"
                MessageHandler(filters.Regex("^Посмотреть карты$"), handle_view_cards),
                MessageHandler(filters.Regex("^Назад$"), handle_back_button)  # Кнопка "Назад"
            ],
            WAITING_FOR_ATTEMPTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_attempts_count)]  # Ввод количества попыток
        },
        fallbacks=[]
    )

    # Добавляем обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(conv_handler)  # ConversationHandler для добавления карт
    application.add_handler(conv_handler_user)  # ConversationHandler для работы с пользователем
    application.add_handler(CallbackQueryHandler(handle_pagination_buttons))

    # Специфические обработчики текстовых сообщений
    application.add_handler(MessageHandler(filters.Regex("^Получить карту$"), get_map))
    application.add_handler(MessageHandler(filters.Regex("^Мои карты$"), show_my_cards))
    application.add_handler(MessageHandler(filters.Regex("^Удалить карту$"), handle_delete_card))
    application.add_handler(MessageHandler(filters.Regex("^Назад$"), handle_back_button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_delete_card_id))

    # Общий обработчик текстовых сообщений должен быть последним
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Добавляем обработчик ошибок
    # application.add_error_handler(error_handler)

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
