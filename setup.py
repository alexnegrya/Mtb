import os
os.system("pip3 install requests")
import requests
import zipfile
import sqlite3
import glob
import signal
import sys

# Убираем вывод о прерывание
signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

system = os.uname().sysname

if system == "Linux" or system == "Windows":
    print(
        "Приветсвуем вас в полуавтоматическом устоновщике Кумэтру бота версии 1.0\nНажмите ENTER для начала устоновке"
    )
    input()
    requirements = [
        "PyMySQL",
        "pyowm",
        "wikipedia",
        "DateTime",
        "beautifulsoup4",
        "pyTelegramBotAPI",
        "flask",
        "lxml",
    ]
    # Спрашиваем у пользователя нужные данные
    bot_token = input("Напишите токен взятый у @BotFather:")
    weather_token = input("Напишите токен взятый у openweathermap.org:")
    secret_key = input("Укажите пароль для админки:")
    # Просим человека дать ответ которые в вариантах
    while True:
        db = input("Какую базу данных вы хотите использовать mysql или sqlite?:")
        if db == "sqlite" or db == "mysql":
            break
        else:
            print("Введите то что указано в списке")
    # Указываем какие файлы на py должны быть
    files = ["main.py", "setup.py", "config.py", "web.py"]
    # Смотрим файлы в папке
    files_dir = glob.glob("*.py")
    # Если нет в папке этих файлов устонавливаем их
    if files_dir != files:
        url = "https://github.com/roaldiopi/Kumatru/archive/main.zip"
        r = requests.get(url)
        with open("main.zip", "wb") as code:
            code.write(r.content)
        # Разахривируем файлы
        zip = zipfile.ZipFile("main.zip")
        zip.extractall()
        zip.close()
        # Удаляем zip архива
        os.remove("main.zip")
    if db == "sqlite":
        sqlite = True
        # Указываем данные по умолчанию
        mysql_user = "user"
        mysql_password = "password"
        mysql_db = "db"
    else:
        sqlite = False
        mysql_user = input("Напишите имя пользователя для базы данных mysql:")
        mysql_password = input("Укажите пароль для базы данных mysql:")
        mysql_db = input("Укажите базу данных mysql:")

    config = (
        """from datetime import datetime
#Из модуля pyowm utils получаем функцию для получения стандартного конфига
from pyowm.utils.config import get_default_config
#Токен взятый с @BotFather
token = '"""+ bot_token + """'
#Токен взятый с сайта openweathermap.org
weather_token = '"""+ weather_token + """'
#Получаем стандартный конфиг для pyowm
config_dict = get_default_config()
#Устонавливаем русский язык в этом конфиге
config_dict['language'] = 'ru'
#Сообщение при старте
on_start_msg = 'Бот запустился'
#Сколько показывать новостей
global_iteration_news = 10
#Секретный ключ для входа в админ панель
admin_password = '"""+ secret_key + """'
#Частота чтения логов
log_reading_frequency = 30000
#База данных sqlite
sqlite="""+ str(sqlite) +"""
#Пользователь к базе данных mysql
mysql_user = '"""+ mysql_user + """'
#Пароль к пользователю mysql
#Если пароль password значит пароль не был устоновлен
mysql_password = '"""+ mysql_password + """'
#База данных mysql
mysql_db = '"""+ mysql_db + """'
if sqlite==False:
	import pymysql
	#Подключаемся к базе данных
	try:
		con = pymysql.connect('localhost', mysql_user, mysql_password, mysql_db)
	except pymysql.err.OperationalError:
		functions.write_log('''[Ошибка] Невозможно подключиться к базе данных!Проверьте правильность данных для подключенния ['''+str(datetime.now())+''']
''')
		exit(1)
	#Создаём курсор.Курсор нужен для выполнений опереаций с базой данных
	cur = con.cursor()"""
    )
    print("Записаваем ввёденные данные в конфиг")
    with open("Kumatru-main/config.py", "w", encoding="utf-8") as f:
        f.write(config)
    for module in requirements:
        os.system("pip3 install "+module)
    if system == "Linux":
        if db == "mysql":
            os.system("apt install mysql")
            print(
                """Итак мы почти закончили осталось два шага
1)Зайти в mysql shell(что устоновщик сделает)
2)Выполнить команды(что вам придеться сделать):
CREATE USER '"""+ mysql_password + """'@'localhost' IDENTIFIED BY '"+db_key+"';
GRANT ALL PRIVILEGES ON * . * TO '"""+ mysql_user+ """'@'localhost';
CREATE DATABASE """+ mysql_db + """;
USE """+ mysql_db + """;
CREATE TABLE user_subscriptions (Chat_Id INT,Username TEXT,first_name TEXT,last_name TEXT,Registration_date TEXT);
CREATE TABLE subscriptions(Month TEXT,Subscriptions INTEGER)
12 раз повторить команду:
INSERT INTO subscriptions(Month,Subscriptions) VALUES ('Изменяем число на +1 пока не будет 12',0);
Нажмите ENTER чтобы продолжить
"""
            )
            input()
            os.system("sudo mysql")
        else:
            conn = sqlite3.connect("Kumatru-main/db.db")
            c = conn.cursor()
            # Создаём таблицу с пользователями
            c.execute(
                "CREATE TABLE users(Chat_Id INTEGER,Username TEXT,first_name TEXT,last_name TEXT,Registration_date TEXT)"
            )
            # Создаём таблицу с подписками
            c.execute(
                "CREATE TABLE subscriptions(Month TEXT,Subscriptions INTEGER)"
                )
            # Наполняем таблицу с подписками нужными данными
            for x in range(1, 10):
                c.execute(
                    "INSERT INTO subscriptions(Month,Subscriptions) VALUES ('0"+x+ "',0)"
                )
            conn.commit()
            for x in range(10, 13):
                c.execute(
                    "INSERT INTO subscriptions(Month,Subscriptions) VALUES ('"+x+ "',0)"
                )
            conn.commit()
            # -------------
            print("Устоновка завершена")
            exit()
    else:
        if db == "mysql":
            print("Скачиваем mysql")
            url = "https://dev.mysql.com/get/Downloads/MySQLInstaller/mysql-installer-community-8.0.22.0.msi"
            r = requests.get(url)
            with open("Cumutru-main/mysql.msi", "wb") as code:
                code.write(r.content)
            print(
                """Итак мы почти закончили осталось два шага
1)Зайти в mysql shell(что устоновщик сделает)
2)Выполнить команды(что вам придеться сделать):
CREATE USER '"""+ mysql_password + """'@'localhost' IDENTIFIED BY '"+db_key+"';
GRANT ALL PRIVILEGES ON * . * TO '"""+ mysql_user + """'@'localhost';
CREATE DATABASE """+ mysql_db + """;
USE """+ mysql_db + """;
CREATE TABLE user_subscriptions (Chat_Id INT,Username TEXT,first_name TEXT,last_name TEXT,Registration_date TEXT);
CREATE TABLE subscriptions(Month TEXT,Subscriptions INTEGER)
12 раз повторить команду:
INSERT INTO subscriptions(Month,Subscriptions) VALUES ('Изменяем число на +1 пока не будет 12',0);
Нажмите ENTER чтобы продолжить
"""
            )
            input()
            exit()
        else:
            conn = sqlite3.connect("Kumutru-main/db.db")
            c = conn.cursor()
            c.execute(
                "CREATE TABLE users(Chat_Id INTEGER,Username TEXT,first_name TEXT,last_name TEXT,Registration_date TEXT)"
            )
            # Создаём таблицу с подписками
            c.execute(
                "CREATE TABLE subscriptions(Month TEXT,Subscriptions INTEGER)"
                )
            # Наполняем таблицу с подписками нужными данными
            for x in range(1, 10):
                c.execute(
                    "INSERT INTO subscriptions(Month,Subscriptions) VALUES ('0"+str(x)+"',0)"
                )
            conn.commit()
            for x in range(10, 13):
                c.execute(
                    "INSERT INTO subscriptions(Month,Subscriptions) VALUES ('"+str(x)+ "',0)"
                )
            conn.commit()
            # -------------
            print("Устоновка завершена")
            exit()
else:
    print("Ваша система не подерживаеться")
