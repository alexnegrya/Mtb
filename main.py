#!/usr/bin/env python
# Пытаемся импортировать нужные библеотеки
try:
    import sqlite3
    import telebot
    import config
    import pyowm
    import wikipedia
    import json
    import signal
    import sys
    import sqlite3
    import functions
    import random
    from bs4 import BeautifulSoup as BS

    # Импортируем класс datetime из модуля datetime
    from datetime import datetime
    from pyowm.utils.config import get_default_config
    from telebot import types
except ModuleNotFoundError:
    functions.write_log(
        "[Ошибка] Какой-то модуль не устоновлен!Перепроверьте список устоновленных модулей ["+ str(datetime.now())+ "]\n"
    )
    exit(1)

# Убираем вывод ошибке о прерывание
signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))
# Инциализация бота
bot = telebot.TeleBot(config.token)
owm = pyowm.OWM(config.weather_token, config.config_dict)

print(
    "Чтобы начать запуск бота напишите 'Запуск' или напишите 'Настройки' для входа в настройки бота"
)
options = input(":")

if options == "Настройки":
    print(
        """Вы вошли в настройки,чтобы изменить какие-то значения используйте config.переменная = 'ваше значение'.
Список доступных переменных:
1)token
2)weather_token
3)on_start_msg
4)global_iteration_news
5)sqlite
6)admin_password
7)log_reading_frequency
8)mysql_user
9)mysql_password
10)mysql_db 
Измения будут приняты ТОЛЬКО для этого запуска"""
    )
    exec(input(":"))
    options = "Запуск"
if options == "Запуск":
    # Смотрим если есть сообщение при старте
    if config.on_start_msg != "":
        if config.sqlite == True:
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            cur.execute("SELECT Chat_id FROM users")
            rows = cur.fetchall()
            for row in rows:
                bot.send_message(row[0], config.on_start_msg)
            con.close()
        else:
            # Если есть сообщение то смотрим все чат айди
            config.cur.execute("SELECT Chat_Id FROM `user_subscriptions`")
            rows = config.cur.fetchall()
            # И в цикле выводим  сообщение при старте в чаты
            for row in rows:
                bot.send_message(row[0], config.on_start_msg)
    # Выводим лог
    functions.write_log(
        "[Консоль] Бот запущен и работает [" + str(datetime.now()) + "]\n"
    )
    # Функция на команду старт
    @bot.message_handler(commands=["start"])
    def welcome(message):
        # Если у пользователя нету имени то соединяем его имя и фамилию
        if message.from_user.username == None:
            message.from_user.username = (
                message.from_user.first_name + "_" + message.from_user.last_name
            )
        # Выводим лог
        functions.write_log(
            "[Консоль] "+ message.from_user.username + " использовал команду start [" + str(datetime.now()) + "]\n"
        )
        # Создаём клавиатуру
        # Подгоняем по размерам
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # Кнопки клавиатуры
        item1 = types.KeyboardButton("Погода")
        item2 = types.KeyboardButton("Новости")
        item3 = types.KeyboardButton("Школа")
        item4 = types.KeyboardButton("Цитата")
        # Добовляем кнопки
        markup.add(item1, item2, item3, item4)
        # Ответ на команду /start
        bot.send_message(
            message.chat.id, "Привет странник!\nЧего изволишь?", reply_markup=markup
        )
        date = datetime.now()
        month = date.strftime("%m")
        if config.sqlite == True:
            # Подключаемся к базе данных sqlite
            con = sqlite3.connect("db.db")
            # Создаём курсор
            cur = con.cursor()
            # Ищем пользователя у которого такой chat id
            cur.execute(
                "SELECT * FROM users Where Chat_id = '" + str(message.chat.id) + "'"
            )
            # Выносим результат из базы
            row = cur.fetchall()
            # Смотрим длину результат
            user = len(row)
            # 0-Пользователя нет
            # 1-есть
            # Если пользователя нет то заносим его базу данных sqlite
            if user == 0:
                cur.execute(
                    "UPDATE subscriptions SET subscriptions = subscriptions+1 WHERE Month = '" + month + "'"
                )
                con.commit()
                cur.execute(
                    """INSERT INTO users(Chat_Id,Username,first_name,last_name,Registration_date) 
VALUES ("""
                    + str(message.chat.id)
                    + """,'"""
                    + message.from_user.username
                    + """','"""
                    + message.from_user.first_name
                    + """','"""
                    + message.from_user.last_name
                    + """','"""
                    + functions.get_date()
                    + """')"""
                )
                con.commit()
                functions.write_log(
                    "[База данных] Добавлен новый пользователь в базу данных [" + str(datetime.now()) + "]\n"
                )
                con.close()
        else:
            # Смотрим нету ли пользователя в базе данных mysql
            user_db = config.cur.execute(
                "SELECT * FROM `user_subscriptions` Where Chat_Id='"+ str(message.chat.id) + "'"
            )
            # Если нету добовляем
            if user_db == 0:
                config.cur.execute(
                    "INSERT INTO `user_subscriptions` (`Chat_Id`, `Username`,`first_name`,`last_name`,`Registration_date`) VALUES (%s,%s,%s,%s,%s)",
                    (
                        message.chat.id,
                        message.from_user.username,
                        message.from_user.first_name,
                        message.from_user.last_name,
                        functions.get_date(),
                    ),
                )
                config.con.commit()
                functions.write_log(
                    "[База данных] Добавлен новый пользователь в базу данных ["+ str(datetime.now()) + "]\n"
                )

    @bot.message_handler(content_types=["text"])
    def main(message):
        # Если у пользователя нету имени то соединяем его имя и фамилию
        if message.from_user.username == None:
            message.from_user.username = (
                message.from_user.first_name + "_" + message.from_user.last_name
            )
        # Смотрим что отослал пользователь
        if message.text == "Новости":
            # Выводим лог
            functions.write_log(
                "[Консоль] " + message.from_user.username + " использовал кнопку новости [" + str(datetime.now()) + "]\n"
            )
            # Парсим сайт point.md
            r_html = functions.get_html("https://point.md/")
            # Указываем что будем парсить и каким парсером
            # lxml-хороший быстрый парсер
            # html.parser - простой но позволяет работать со сломанными тэгами типо div></div
            html = BS(r_html, "lxml")
            posts = []
            # В цикле собираем все заголовки время и ссылки в массив
            for el in html.select(".post-list-container-item"):
                title = el.select(".post-list-container-item-text-title > a")
                time = el.select(".post-list-time")
                links = [a["href"] for a in el.find_all("a", href=True) if a.text]
                posts.append(
                    {"title": title[0].text, "time": time[0].text, "href": links[0]}
                )
            # Также в цикле отсылаем сообщения с новостями
            for post in posts[0 : config.global_iteration_news]:
                bot.send_message(
                    message.chat.id,
                    post["title"]
                    + "\nВремя:" + post["time"]
                    + "\nСсылка:https://point.md/"+post["href"],
                )
        elif message.text == "Погода":
            # Выводим лог
            functions.write_log(
                "[Консоль] " + message.from_user.username + " использовал кнопку Погода [" + str(datetime.now()) + "]\n"
            )
            msg = bot.send_message(message.chat.id, "Введи название города")
            bot.register_next_step_handler(msg, weather)
        elif message.text == "Школа":
            # Выводим лог
            functions.write_log(
                "[Консоль] "+ message.from_user.username + " использовал кнопку школа [" + str(datetime.now()) + "]\n"
            )
            msg_school = bot.send_message(
                message.chat.id,
                "Что вам нужно?:\n1)Калькулятор\n2)Быстрый поиск в вики\nВыбери нужный вариант и отошли мне",
            )
            bot.register_next_step_handler(msg_school, school)
        elif message.text == "Цитата":
            # Выводим лог
            functions.write_log(
                "[Консоль] "+ message.from_user.username+ " использовал кнопку цитата ["+ str(datetime.now())+ "]\n"
            )
            quote = functions.file("", "quotes.json", "json", "r")
            rand_int = random.randint(0, 10266)
            msg = (
                "Цитата:" + quote[rand_int]["quote"]
                +"\nАвтор:"+ quote[rand_int]["source"]
            )
            # Отсылаем цитату
            bot.send_message(message.chat.id, msg)
        elif message.text == config.admin_password:
            msg = bot.send_message(
                message.chat.id,
                """Добро пожаловать в администраторскую панель
Доступные опции:
1)Отослать сообщение во все чаты
2)Отослать сообщение определенному человеку""",
            )
            functions.write_log(
                "[Админ панель] " + message.from_user.username + " зашёл в администраторскую  панель [" + str(datetime.now()) + "]\n"
            )
            bot.register_next_step_handler(msg, admin)
        else:
            msg = bot.send_message(message.chat.id, "Ваш запрос не понятен")

    def admin(message):
        try:
            command = message.text
            if command == "1":
                msg = bot.send_message(
                    message.chat.id, "Какое сообщение вы хотите отослать"
                )
                bot.register_next_step_handler(msg, admin_send_msg_to_all)
            elif command == "2":
                msg = bot.send_message(
                    message.chat.id, "Кому вы хотите отослать сообщение"
                )
                bot.register_next_step_handler(msg, admin_send_msg_step_1)
            else:
                bot.register_next_step_handler(msg, "Введите то что в списке")
        except:
            bot.send_message(message.chat.id, "Введите то что в списке")

    # Первая функция смотрим chat id
    def admin_send_msg_step_1(message):
        global chat_id, who
        who = message.text
        if config.sqlite == True:
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            cur.execute("SELECT Chat_id FROM users Where Username = '" + who + "'")
            chat_id = cur.fetchone()
            length_chat_id = len(chat_id)
            if length_chat_id == 1:
                msg = bot.send_message(
                    message.chat.id, "Какое сообщение вы хотите отослать"
                )
                bot.register_next_step_handler(msg, admin_send_msg_step_2)
            else:
                bot.send_message(message.chat.id, "Пользователь не найден")
        else:
            config.cur.execute(
                "SELECT `Chat_Id` FROM `users` Where `Username`='" + who + "'"
            )
            chat_id = config.cur.fetchone()
            if chat_id == None:
                bot.send_message(message.chat.id, "Пользователь не найден")
            else:
                msg = bot.send_message(
                    message.chat.id, "Какое сообщение вы хотите отослать"
                )
                bot.register_next_step_handler(msg, admin_send_msg_step_2)

    # Вторая функция отправляем сообщение
    def admin_send_msg_step_2(message):
        if message.from_user.username == None:
            message.from_user.username = "Неизвестный"
        msg = message.text
        bot.send_message(chat_id[0], msg)
        bot.send_message(message.chat.id, "Сообщение отправленно")
        functions.write_log(
            "[Админ] "+ message.from_user.username + " отравил сообщение " + msg + " пользователю " + who+ " ["+ str(datetime.now()) + "]\n"
        )

    # ------------
    # Функция для отсылки сообщений всем пользователем бота
    def admin_send_msg_to_all(message):
        admin_message = message.text
        functions.write_log(
            "[Админ] " + admin_message + " [" + str(datetime.now()) + "]\n"
        )
        config.cur.execute("SELECT Chat_Id FROM `users`")
        rows = config.cur.fetchall()
        # И в цикле выводим  сообщение при старте в чаты
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
            # Решаем уравнение но убираем возможность импортировать модули
            answer = eval(msg, {"__builtins__": {}})
            bot.send_message(message.chat.id, answer)
        except:
            # Если ошибка отсылаем сообщение
            bot.send_message(message.chat.id, "Что то не так")

    def wiki(message):
        try:
            search = message.text
            # Ставим русскикй язык
            wikipedia.set_lang("ru")
            # Отсылаем wiki текст
            bot.send_message(message.chat.id, wikipedia.summary(search, sentences=5))
        except:
            # Если нечего не найдено отсылаем что нечего не найдено
            bot.send_message(message.chat.id, "Нечего не найдено")

    def weather(message):
        try:
            town = message.text
            mgr = owm.weather_manager()
            # Смотрим погоду
            observation = mgr.weather_at_place(town)
            w = observation.weather
            # Смотрим также ветер и температу
            wind = w.wind()
            temp = w.temperature("celsius")
            bot.send_message(
                message.chat.id,
                "Город:"+ town
                + "\nСтатус:"+ w.detailed_status
                + "\nТемпература:"+ str(temp["temp"])+ "°"
                + "\nОщущаеться как:"+ str(temp["feels_like"])+ "°"
                + "\nСкорость ветра:"+ str(wind["speed"])+ " м/с",
            )
        except pyowm.commons.exceptions.UnauthorizedError:
            functions.write_log(
                "[Ошибка] Запрос не был выполнен так как неправильный api ключ ["+ str(datetime.now()) + "]\n"
                )
            bot.send_message(message.chat.id, "Произошла внутрения ошибка")
        except:
            bot.send_message(message.chat.id, "Город не найден")

    bot.polling(none_stop=True)
else:
    print("Напишите значения из списка")
