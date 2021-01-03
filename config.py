import functions
# Из модуля datetime импортируем класс datetime
from datetime import datetime
# Из модуля pyowm utils получаем функцию для получения стандартного конфига
from pyowm.utils.config import get_default_config
# Токен взятый с @BotFather
token = "1446670433:AAEUVbmj3iZsK-ZYLapI9SPr13DfMurRW44"
# Токен взятый с сайта openweathermap.org
weather_token = "2f3a07a16302c4c464ab42cd11a6b27b"
# Получаем стандартный конфиг для pyowm
config_dict = get_default_config()
# Устонавливаем русский язык в этом конфиге
config_dict["language"] = "ru"
# Сообщение при старте
on_start_msg = "Бот запустился"
# Сколько показывать новостей
global_iteration_news = 30
# Секретный ключ для входа в админ панель
admin_password = "peligas5"
# Частота чтения логов
log_reading_frequency = 30000
# База данных sqlite
sqlite = True
# Пользователь к базе данных mysql
mysql_user = "bot"
# Пароль к пользователю mysql
mysql_password = "peligas5"
# База данных mysql
mysql_db = "telegram"
if sqlite == False:
    import pymysql

    # Подключаемся к базе данных
    try:
        con = pymysql.connect("localhost", mysql_user, mysql_password, mysql_db)
    except pymysql.err.OperationalError:
        functions.write_log('''[Ошибка] Невозможно подключиться к базе данных!Проверьте правильность данных для подключенния ['''+str(datetime.now())+''']
'''
        )
        exit(1)
    # Создаём курсор.Курсор нужен для выполнений операций с базой данных
    cur = con.cursor()
