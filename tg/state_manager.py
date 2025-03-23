# Глобальный словарь для хранения текущего индекса карты для каждого пользователя
user_current_index = {}

# Функция для получения текущего индекса
def get_current_index(user_id):
    return user_current_index.get(user_id, 0)

# Функция для установки текущего индекса
def set_current_index(user_id, index):
    user_current_index[user_id] = index
