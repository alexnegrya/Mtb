import os
import signal
import sys
import zipfile
from platform import system
print("Устонавливаем requests")
os.system("pip install requests -q")
import requests

# Убираем вывод о прерывание
signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))
system = system()

if system == "Linux" or system == "Windows":
    print(
        "Приветсвуем вас в полуавтоматическом устоновщике Кумэтру бота версии 1.0\nНажмите ENTER для начала устоновке"
    )
    input()
    # Спрашиваем у пользователя нужные данные
    bot_token = input("Напишите токен взятый у @BotFather:")
    weather_token = input("Напишите токен взятый у openweathermap.org:")
    admin_login = input("Укажите логин для админки:")
    admin_password = input("Укажите пароль для админки:")
    requirements = [
        "pyowm",
        "wikipedia",
        "beautifulsoup4",
        "pyTelegramBotAPI",
        "flask",
        "pymongo==3.11.2"
    ]
    # Проверка скачен ли архив с файлами
    directory = os.listdir(path=".")
    if 'main.py' in directory:
        downloaded = True
    else:
        downloaded = False
    if downloaded is False:
        print("Скачиваем архив")
        url = "https://github.com/roaldiopi/Mtb/archive/main.zip"
        r = requests.get(url)
        with open("main.zip", "wb") as f:
            f.write(r.content)
        # Разархивируем файлы
        print("Разархивируем файлы")
        zip_archive = zipfile.ZipFile("main.zip")
        zip_archive.extractall()
        zip_archive.close()
        # Удаляем zip
        print("Удаляем zip файл")
        os.remove("main.zip")
    config = (
            """from pymongo import MongoClient
# Из модуля pyowm utils получаем функцию для получения стандартного конфига
from pyowm.utils.config import get_default_config

# Соединяемся с базой данных
client = MongoClient('localhost', 27017)
db = client.Telegram
users = db.users
admins = db.admins
chat = db.chat
# Токен взятый с @BotFather
token = '""" + bot_token + """'
# Токен взятый с сайта openweathermap.org
weather_token = '""" + weather_token + """'
# Получаем стандартный конфиг для pyowm
config_dict = get_default_config()
# Устонавливаем русский язык в этом конфиге
config_dict['language'] = 'ru'
# Сообщение при старте
on_start_msg = 'Бот запустился'
# Сколько показывать новостей
global_iteration_news = 0
# Секретный ключ для входа в админ панель
admin_password = '""" + admin_password + """'
# Частота чтения логов
log_reading_frequency = 30000"""
    )
    print("Записаваем ввёденные данные в конфиг")
    if downloaded is True:
        with open("config.py", "w", encoding="utf-8") as f:
            f.write(config)
        print("config записан")
    else:
        with open("Mtb-main/config.py", "w", encoding="utf-8") as f:
            f.write(config)
    print("Устонавливаем необходимые зависимости")
    for module in requirements:
        os.system("pip3 install " + module + " -q")
    if system == "Linux":
        print("""Осталось несколько шагов чтобы устоновить бота
1)Устоновить mongodb
2)Создать базу данных "Telegram"
3)Создать в базе данных три коллекции users,chat,admins
4)Создать документ в коллекции admins с полями login,password(хэшированный в md5),level(0=Супер админ,1=Админ)""")
        print("Устоновка завершена")
    else:
        r = requests.get("https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-4.4.3-signed.msi")
        with open("mongo.msi", "wb") as content:
            content.write(r.content)
        print("""Осталось несколько шагов чтобы устоновить бота
1)Устоновить mongodb
2)Создать базу данных "Telegram"
3)Создать в базе данных три коллекции users,chat,admins
4)Создать документ в коллекции admins с полями login,password(хэшированный в md5),level(0=Супер админ,1=Админ)""")
        print("Устоновка завершена")

else:
    print("Ваша система не подерживаеться")
