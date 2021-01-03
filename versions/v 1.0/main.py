#!/usr/bin/env python
#Импортируем нужные библеотеки
import telebot,config,pyowm,requests,wikipedia,json
from bs4 import BeautifulSoup as BS
from pyowm.utils.config import get_default_config
from telebot import types


config_dict = get_default_config()
config_dict["language"] = "ru"

#Настройки для бота
bot = telebot.TeleBot(config.token)
owm = pyowm.OWM(config.weather_token, config_dict)
print("Чтобы начать запуск бота напишите 'Запуск'")
options = input(":")
if options == "Запуск":
	print("Бот запущен и работает")
	#Функция на команду старт
	@bot.message_handler(commands=["start"])
	def welcome(message):
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

	@bot.message_handler(content_types=["text"])
	def main(message):
		#Смотрим что отослал пользователь
		if message.text == "Новости":
			bot.send_message(message.chat.id, "Новости:")
			r = requests.get('https://point.md/ru/novosti/obschestvo/')
			html = BS(r.content, 'html.parser')
			for el in html.select('.post-list-container-item'):
				title = el.select('.post-list-container-item-text-title > a')
				time = el.select('.post-list-time')
				links_with_text = [a['href'] for a in el.find_all('a', href=True) if a.text]
				bot.send_message(message.chat.id,
					title[0].text+
					"\nВремя:"+time[0].text+
					"\nСсылка:https://point.md/"+links_with_text[0])
		elif message.text == "Погода":
			msg = bot.send_message(message.chat.id, "Введи название города")
			#Отсылаем сообщение и указываем куда перейти после ответа
			bot.register_next_step_handler(msg, weather)
		elif message.text == "Школа":
			msg_school = bot.send_message(message.chat.id, 
				"Что вам нужно?:\n1)Калькулятор\n2)Быстрый поиск в вики\nВыбери нужный вариант и отошли мне")
			bot.register_next_step_handler(msg_school, school)
		elif message.text == "Цитата":
			r = requests.post('http://api.forismatic.com/api/1.0/', data = {'method':'getQuote','lang':'ru','format':'json'})
			quote = r.json()
			bot.send_message(message.chat.id, quote['quoteText'])
		else:
			msg = bot.send_message(message.chat.id, "Ваш запрос не понятен")

	def school(message):
		text = message.text
		if text == "Калькулятор":
			msg = bot.send_message(message.chat.id, "Введи числа:")
			bot.register_next_step_handler(msg, calculator)
		elif text == "Быстрый поиск в вики":
			msg = bot.send_message(message.chat.id, "Что найти в вики?:")
			bot.register_next_step_handler(msg, wiki)
		else:
			bot.send_message(message.chat.id, "Введи то что указоно в списки!")
	def calculator(message):
		try:
			msg = message.text
			answer = eval(msg, {'__builtins__':{}})
			bot.send_message(message.chat.id, answer)
		except:
			bot.send_message(message.chat.id, "Что то не так")

	def wiki(message):
		try:
			search = message.text
			wikipedia.set_lang("ru")
			bot.send_message(message.chat.id, wikipedia.summary(search, sentences=5))
		except:
			bot.send_message(message.chat.id, "Запрос не найден")

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
				"\nСкорость ветра:"+str(wind['speed'])+" м/с"+
				"\nОщущаеться как:"+str(temp['feels_like'])+"°")
		except:
			bot.send_message(message.chat.id, "Город не найден")


	bot.polling(none_stop=True)

