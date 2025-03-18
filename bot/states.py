from telegram.ext import ConversationHandler

# Определяем состояния для добавления карты
WAITING_FOR_IMAGE, WAITING_FOR_NAME, WAITING_FOR_RARITY, WAITING_FOR_STYLE, WAITING_FOR_PNAME = range(5)

# Определяем состояния для выдачи попыток
WAITING_FOR_USERNAME = 5
WAITING_FOR_ATTEMPTS = 6
WAITING_FOR_CARD_ID = 7

# Экспортируем все состояния
__all__ = [
    'WAITING_FOR_IMAGE',
    'WAITING_FOR_NAME',
    'WAITING_FOR_RARITY',
    'WAITING_FOR_STYLE',
    'WAITING_FOR_PNAME',
    'WAITING_FOR_USERNAME',
    'WAITING_FOR_ATTEMPTS',
    'WAITING_FOR_CARD_ID'
]
