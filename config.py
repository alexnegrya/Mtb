import pymysql
#Из модуля pyowm utils получаем функцию для получения стандартного конфига
from pyowm.utils.config import get_default_config
#Подключаемся к базе данных
con = pymysql.connect('localhost', 'bot', 
    'peligas5', 'telegram')
#Создаём курсор.Курсор нужен для выполнений опереаций с базой данных
cur = con.cursor()
#Токен взятый с @BotFather
token = '1470281360:AAE7zCSqaAmV2dsmtqfHQ8zd1G0WRhVWoEA'
#Токен взятый с сайта openweathermap.org
weather_token = '2f3a07a16302c4c464ab42cd11a6b27b'
#Получаем стандартный конфиг для pyowm
config_dict = get_default_config()
#Устонавливаем русский язык в этом конфиге
config_dict["language"] = "ru"
#Сообщение при старте
on_start_msg = "Бот запустился"
#Сколько показывать новостей
global_iteration_news = 10
#Секретный ключ для входа в админ панель
admin_key = "peligas5"
