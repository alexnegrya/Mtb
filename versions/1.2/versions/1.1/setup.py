import os
import requests
import zipfile
import sqlite3
system = os.uname().sysname

if system == "Linux" or system == "Windows":
	print("Приветсвуем вас в полуавтоматическом устоновщике Кумэтру бота версии 0.5\nНажмите ENTER для начала устоновке")
	input()
	requirements = ["PyMySQL","pyowm","requests","wikipedia" ,"DateTime","beautifulsoup4","pyTelegramBotAPI"]
	bot_token = input("Напишите токен взятый у @BotFather:")
	weather_token = input("Напишите токен взятый у openweathermap.org:")
	secret_key = input("Укажите пароль для админки:")
	while True:
		db = input("Какую базу данных вы хотите использовать mysql или sqlite?:")
		if db == "sqlite" or db == "mysql":
			break
		else:
			print("Введите то что указано в списке")
	url = "https://github.com/roaldiopi/Cumutru/archive/main.zip"
	r = requests.get(url)
	with open("main.zip", "wb") as code:
		code.write(r.content)
	zip = zipfile.ZipFile('main.zip')
	zip.extractall()
	zip.close()
	db_key = "password"
	config = "import pymysql\n#Из модуля pyowm utils получаем функцию для получения стандартного конфига\nfrom pyowm.utils.config import get_default_config\n#Подключаемся к базе данных\ncon = pymysql.connect('localhost', 'bot', '"+db_key+"', 'telegram')\n#Создаём курсор.Курсор нужен для выполнений опереаций с базой данных\ncur = con.cursor()\n#Токен взятый с @BotFather\ntoken = '"+bot_token+"'\n#Токен взятый с сайта openweathermap.org\nweather_token = '"+weather_token+"'\n#Получаем стандартный конфиг для pyowm\nconfig_dict = get_default_config()\n#Устонавливаем русский язык в этом конфиге\nconfig_dict['language'] = 'ru'\n#Сообщение при старте\non_start_msg = 'Бот запустился'\n#Сколько показывать новостей\nglobal_iteration_news = 10\n#Секретный ключ для входа в админ панель\nadmin_key = '"+secret_key+"'"
	if db == "sqlite":
		requirements.pop(0)
		config =  config + "\nsqlite=True"
	else:
		db_key = input("Укажите пароль для базы данных mysql:")
	for module in requirements:
		os.system("pip3 install "+module)
	if system == "Linux":
		print("Записаваем ввёденные данные в файл")
		handle = open("Cumutru-main/config.py", "a")
		handle.write(config)
		handle.close()
		if db == "mysql":
			#os.system("apt install mysql")
			print("Итак мы почти закончили осталось два шага\n1)Зайти в mysql shell(что устоновщик сделает)\n2)Выполнить команды(что вам придеться сделать):\nCREATE USER 'bot'@'localhost' IDENTIFIED BY '"+db_key+"';\nGRANT ALL PRIVILEGES ON * . * TO 'bot'@'localhost';'\nCREATE DATABASE telegram;\nCREATE TABLE users (Chat_Id INT,Username TEXT);\nНажмите ENTER чтобы продолжить")
			input()
			#os.system("sudo mysql")
		else:
			conn = sqlite3.connect("Cumutru-main/db.db")
			c = conn.cursor()
			c.execute("CREATE TABLE users(Chat_Id INTEGER,Username TEXT)")
			print("Устоновка завершена")
			exit()
	else:
		print("Записаваем ввёденные данные в файл")
		handle = open("Cumutru-main/config.py", "a")
		handle.write(config)
		handle.close()
		if db == "mysql":
			print("Скачиваем mysql")
			url = "https://dev.mysql.com/get/Downloads/MySQLInstaller/mysql-installer-community-8.0.22.0.msi"
			r = requests.get(url)
			with open("Cumutru-main/mysql.msi", "wb") as code:
				code.write(r.content)
			print("Итак мы почти закончили осталось два шага\n1)Устновить mysql путём открытия файла mysql.msi\n2)Зайти mysql shell\n2)Выполнить команды(что вам придеться сделать):\nCREATE USER 'bot'@'localhost' IDENTIFIED BY 'peligas5';\nGRANT ALL PRIVILEGES ON * . * TO 'bot'@'localhost';'\nCREATE DATABASE telegram;\nCREATE TABLE users (Chat_Id INT,Username TEXT);\nНажмите ENTER чтобы выйти")
			input()
			exit()
		else:
			import sqlite3
			conn = sqlite3.connect("Cumutru-main/db.db")
			c = conn.cursor()
			c.execute("CREATE TABLE users(Chat_Id INTEGER,Username TEXT)")
			print("Устоновка завершена")
			exit()
else:
	print("Ваша система не подерживаеться")

