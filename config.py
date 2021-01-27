from pymongo import MongoClient
# Из модуля pyowm utils получаем функцию для получения стандартного конфига
from pyowm.utils.config import get_default_config

# Соединяемся с базой данных
client = MongoClient('localhost', 27017)
db = client.Telegram
users = db.users
admins = db.admins
chat = db.chat
# Токен взятый с @BotFather
token = '1414923910:AAExc7iCPRK-RfiZJ0Tv-Jda3DVqIn0e9yY'
# Токен взятый с сайта openweathermap.org
weather_token = '2f3a07a16302c4c464ab42cd11a6b27b'
# Получаем стандартный конфиг для pyowm
config_dict = get_default_config()
# Устонавливаем русский язык в этом конфиге
config_dict['language'] = 'ru'
# Сообщение при старте
on_start_msg = 'Бот запустился'
# Сколько показывать новостей
global_iteration_news = 300
# Секретный ключ для входа в админ панель
admin_password = 'peligas5'
# Частота чтения логов
log_reading_frequency = 30000