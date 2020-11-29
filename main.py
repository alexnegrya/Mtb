#!/usr/bin/env python
#Пытаемся импортировать нужные библеотеки
try:
	import telebot
	import config
	import pyowm
	import requests
	import wikipedia
	import json
	import signal
	import sys
	from bs4 import BeautifulSoup as BS
	#Импортируем класс datetime из модуля datetime
	from datetime import datetime
	from pyowm.utils.config import get_default_config
	from telebot import types
except:
	print("Ошибка с модулями!Устоновите их или обновите")
	exit()



#Убираем вывод ошибке о прерывание
signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))
#Инциализация бота и погоды
bot = telebot.TeleBot(config.token)
owm = pyowm.OWM(config.weather_token, config.config_dict)
print("Чтобы начать запуск бота напишите 'Запуск' или напишите 'Настройки' для входа в настройки бота")
options = input(":")
if options == "Настройки":
	print(
		"Вы вошли в настройки чтобы изменить какие-то значения используйте config.var = 'ваше значение'.\nСписок доступных переменных:\n1)token\n2)weather_token\n3)on_start_msg\n4)global_iteration_news\nИзмения будут приняты ТОЛЬКО для этого запуска"
		)
	exec(input(":"))
	options = "Запуск"
if options == "Запуск":
	#Смотрим если есть сообщение при старте
	if config.on_start_msg != "":
		#Если есть сообщение то смотрим все чат айди 
		config.cur.execute("SELECT Chat_Id FROM `users`")
		rows = config.cur.fetchall()
		#И в цикле выводим  сообщение при старте в чаты
		for row in rows:
			bot.send_message(row[0], config.on_start_msg)
	start = "[Консоль]Бот запущен и работает ["+str(datetime.now())+"]\n"
	print("[Консоль]Бот запущен и работает ["+str(datetime.now())+"]")
	handle = open("logs.txt", "a")
	handle.write(start)
	handle.close()
	#Функция на команду старт
	@bot.message_handler(commands=["start"])
	def welcome(message):
		#Если у пользователя нету имени то даём ему имя 'Неизвестный'
		if message.from_user.username == None:
			message.from_user.username = "Неизвестный"
		#Пишем лог в переменную
		log_c = "[Консоль] "+ message.from_user.username + " использовал команду start ["+str(datetime.now())+"]\n"
		#Выводим лог
		print("[Консоль] "+ message.from_user.username + " использовал команду start ["+str(datetime.now())+"]")
		#Пишем лог в файл
		handle = open("logs.txt", "a")
		handle.write(log_c)
		handle.close()
		#Создаём клавиатуру
		#Подгоняем по размерам
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	    #Кнопки клавиатуры
		item1 = types.KeyboardButton("Погода")
		item2 = types.KeyboardButton("Новости")
		item3 = types.KeyboardButton("Школа")
		item4 = types.KeyboardButton("Цитата")
	    #Добовляем кнопки
		markup.add(item1, item2, item3, item4)
	    #Ответ на команду /start
		bot.send_message(message.chat.id, "Привет странник!\nЧего изволишь?", reply_markup=markup)
		#Смотрим нету ли пользователя в базе данных
		user_db = config.cur.execute("SELECT * FROM `users` Where Chat_Id='"+str(message.chat.id)+"'")
		#Если нету добовляем
		if user_db == 0:
			config.cur.execute(
				"INSERT INTO `users` (`Chat_Id`, `Username`) VALUES (%s,%s)",
				(message.chat.id,message.from_user.username)
				)
			config.con.commit()
			log_d = "[База данных] Добавлен новый пользователь в базу данных ["+str(datetime.now())+"]\n"
			print("[База данных] Добавлен новый пользователь в базу данных ["+str(datetime.now())+"]")
			handle = open("logs.txt", "a")
			handle.write(log_d)
			handle.close()

	@bot.message_handler(content_types=["text"])
	def main(message):
		#Если у пользователя нету имени то даём ему имя 'Неизвестный'
		if message.from_user.username == None:
			message.from_user.username = "Неизвестный"
		#Смотрим что отослал пользователь
		if message.text == "Новости":
			log_n = "[Консоль] "+ message.from_user.username+ " использовал кнопку новости ["+str(datetime.now())+"]\n"
			#Выводим лог
			print("[Консоль] "+ message.from_user.username+ " использовал кнопку новости ["+str(datetime.now())+"]")
			#Пишем лог в файл
			handle = open("logs.txt", "a")
			handle.write(log_n)
			handle.close()
			#Парсим сайт point.md
			r = requests.get('https://point.md/ru/novosti/obschestvo/')
			html = BS(r.content, 'html.parser')
			posts = []
			#В цикле выводим все заголовки статей и их време также мы ещё выводим время статьи
			for el in html.select('.post-list-container-item'):
				title = el.select('.post-list-container-item-text-title > a')
				time = el.select('.post-list-time')
				links = [a['href'] for a in el.find_all('a', href=True) if a.text]
				posts.append({
					'title' : title[0].text, 'time' : time[0].text, 'href' : links[0]
					})
			#Также в цикле отсылаем сообщения с новостями
			for post in posts[0:config.global_iteration_news]:
				bot.send_message(message.chat.id,
						post['title']+
						"\nВремя:"+post['time']+
						"\nСсылка:https://point.md/"+post['href']
						)
		elif message.text == "Погода":
			log_w = "[Консоль] " + message.from_user.username + " использовал кнопку Погода ["+str(datetime.now())+"]\n"
			#Выводим лог
			print("[Консоль] " + message.from_user.username + " использовал кнопку Погода ["+str(datetime.now())+"]")
			#Пишем лог в файл
			handle = open("logs.txt", "a")
			handle.write(log_w)
			handle.close()
			msg = bot.send_message(message.chat.id, "Введи название города")
			bot.register_next_step_handler(msg, weather)
		elif message.text == "Школа":
			log_s = "[Консоль] " + message.from_user.username + " использовал кнопку школа ["+str(datetime.now())+"]\n"
			#Выводим лог
			print("[Консоль] " + message.from_user.username + " использовал кнопку школа ["+str(datetime.now())+"]")
			#Пишем лог в файл
			handle = open("logs.txt", "a")
			handle.write(log_s)
			handle.close()
			msg_school = bot.send_message(message.chat.id, 
				"Что вам нужно?:\n1)Калькулятор\n2)Быстрый поиск в вики\nВыбери нужный вариант и отошли мне")
			bot.register_next_step_handler(msg_school, school)
		elif message.text == "Цитата":
			log_q = "[Консоль] " + message.from_user.username + " использовал кнопку цитата ["+str(datetime.now())+"]\n"
			#Выводим лог
			print("[Консоль] " + message.from_user.username + " использовал кнопку цитата ["+str(datetime.now())+"]")
			#Пишем лог в файл
			handle = open("logs.txt", "a")
			handle.write(log_q)
			handle.close()
			#Отсылаем запрос на сервер цитат
			r = requests.post('http://api.forismatic.com/api/1.0/', data = {'method':'getQuote','lang':'ru','format':'json'})
			#Загружаем json
			quote = r.json()
			#Отсылаем цитату
			bot.send_message(message.chat.id, quote['quoteText'])
		elif message.text == config.admin_key:
			msg = bot.send_message(message.chat.id, "Добро пожаловать в администраторскую панель\nДоступные опции:\n1)Отослать сообщение во все чаты\n2)Отослать сообщение определенному человеку")
			log_s = "[Админ панель] "+message.from_user.username+" зашёл в администраторскую  панель ["+str(datetime.now())+"]\n"
			#Выводим лог
			print("[Админ панель] "+message.from_user.username+" зашёл в администраторскую панель ["+str(datetime.now())+"]")
			#Пишем лог в файл
			handle = open("logs.txt", "a")
			handle.write(log_s)
			handle.close()
			bot.register_next_step_handler(msg, admin)
		else:
			msg = bot.send_message(message.chat.id, "Ваш запрос не понятен")
	def admin(message):
		command = message.text
		if command == "1":
			msg = bot.send_message(message.chat.id, "Какое сообщение вы хотите отослать")
			bot.register_next_step_handler(msg, admin_send_msg_to_all)
		elif command == "2":
			msg = bot.send_message(message.chat.id, "Кому вы хотите отослать сообщение")
			bot.register_next_step_handler(msg, admin_send_msg_part1)
		else:
			bot.register_next_step_handler(msg, "Введите то что в списке")
#Первая функция смотрим chat id
	def admin_send_msg_part1(message):
		global chat_id
		who = message.text
		config.cur.execute("SELECT `Chat_Id` FROM `users` Where `Username`='"+who+"'")
		chat_id = config.cur.fetchone()
		msg = bot.send_message(message.chat.id, "Кокое сообщение вы хотите отослать")
		bot.register_next_step_handler(msg, admin_send_msg_part2)
#Вторая функция отправляем сообщение
	def admin_send_msg_part2(message):
		try:
			msg = message.text
			bot.send_message(chat_id[0], msg)
			bot.send_message(message.chat.id, "Сообщение отправленно")
		except:
			bot.send_message(message.chat.id, "Пользователь не найден")
#------------
#Функция для отсылки сообщений всем пользователем бота
	def admin_send_msg_to_all(message):
		admin_message = message.text 
		log_s = "[Админ] "+admin_message+" ["+str(datetime.now())+"]\n"
		#Выводим лог
		print("[Админ] "+admin_message+" ["+str(datetime.now())+"]")
		#Пишем лог в файл
		handle = open("logs.txt", "a")
		handle.write(log_s)
		handle.close()
		config.cur.execute("SELECT Chat_Id FROM `users`")
		rows = config.cur.fetchall()
		#И в цикле выводим  сообщение при старте в чаты
		for row in rows:
			bot.send_message(row[0], admin_message)

	def school(message):
		text = message.text
		if text == "1":
			msg = bot.send_message(message.chat.id, "Введи числа:")
			bot.register_next_step_handler(msg, calculator)
		elif text == "2":
			msg = bot.send_message(message.chat.id, "Что найти в вики?:")
			bot.register_next_step_handler(msg, wiki)
		else:
			bot.send_message(message.chat.id, "Введи то что указоно в списки!")
	def calculator(message):
		try:
			msg = message.text
			#Решаем уравнение но убираем возможность импортировать модули
			answer = eval(msg, {'__builtins__':{}})
			bot.send_message(message.chat.id, answer)
		except:
			#Если ошибка отсылаем сообщение
			bot.send_message(message.chat.id, "Что то не так")

	def wiki(message):
		try:
			search = message.text
			#Ставим русскикй язык
			wikipedia.set_lang("ru")
			#Отсылаем wiki текст
			bot.send_message(message.chat.id, wikipedia.summary(search, sentences=5))
		except:
			#Если нечего не найдено отсылаем что нечего не найдено
			bot.send_message(message.chat.id, "Нечего не найдено")

	def weather(message):
		try:
			town = message.text
			mgr = owm.weather_manager()
			observation = mgr.weather_at_place(town)
			w = observation.weather
			wind = w.wind()
			temp = w.temperature('celsius')
			bot.send_message(message.chat.id, "Город:"+town+
				"\nСтатус:"+w.detailed_status+
				"\nТемпература:"+str(temp['temp'])+"°"+
				"\nОщущаеться как:"+str(temp['feels_like'])+"°"+
				"\nСкорость ветра:"+str(wind['speed'])+" м/с"
				)
		except:
			bot.send_message(message.chat.id, "Город не найден")

	bot.polling(none_stop=True)
else:
	print("Напишите значения из списка")
