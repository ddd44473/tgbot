from telegram.ext import ConversationHandler

# Определяем состояния
WAITING_FOR_IMAGE, WAITING_FOR_NAME, WAITING_FOR_RARITY, WAITING_FOR_STYLE, WAITING_FOR_PNAME = range(5)

# Экспортируем состояния
__all__ = ['WAITING_FOR_IMAGE', 'WAITING_FOR_NAME', 'WAITING_FOR_PNAME', 'WAITING_FOR_STYLE', 'WAITING_FOR_RARITY']
