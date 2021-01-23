import sys
from lib import Date, write_log
import sqlite3
import json
import telebot
import requests
import pyowm
from pyowm.commons import exceptions
import wikipedia
import signal
import random
from bs4 import FeatureNotFound, BeautifulSoup
from pyowm.utils.config import get_default_config
from telebot import types

# Убираем вывод ошибке о прерывание
signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

print("""
.___  ___. .___________..______   
|   \/   | |           ||   _  \  
|  \  /  | `---|  |----`|  |_)  | 
|  |\/|  |     |  |     |   _  <  
|  |  |  |     |  |     |  |_)  | 
|__|  |__|     |__|     |______/ 
""")

print(
    "Чтобы начать запуск бота напишите 'Запуск'"
)
options = input(":")

if options == "Запуск":
    token = input("Введите телеграмм токен:")
    weather_token = input("Введите owm токен:")
    on_start_msg = input("Введите сообщение при старте:")
    global_iteration_news = input("Введите количество выводимых новостей:")
    admin_password = input("Введите админ пароль:")
    # Получаем стандартный конфиг для pyowm
    config_dict = get_default_config()
    # Устонавливаем русский язык в этом конфиге
    config_dict['language'] = 'ru'
    # Инциализация бота
    bot = telebot.TeleBot(token)
    owm = pyowm.OWM(weather_token, config_dict)
    # Создаём экзампляр класса Date()
    Date = Date()
    # Смотрим если есть сообщение при старте
    if on_start_msg != "":
        con = sqlite3.connect("db.db")
        cur = con.cursor()
        cur.execute("SELECT Chat_id FROM users")
        rows = cur.fetchall()
        for row in rows:
            bot.send_message(row[0], on_start_msg)
        con.close()
    # Выводим лог
    write_log(
        "[Консоль] Бот запущен и работает [" + Date.get_date() + "]\n"
    )

    # Функция на команду старт
    @bot.message_handler(commands=["start"])
    def welcome(message):
        # Если у пользователя нету имени то соединяем его имя и фамилию
        if message.from_user.username is None:
            message.from_user.username = (
                    message.from_user.first_name + "_" + message.from_user.last_name
            )
        # Выводим лог
        write_log(
            "[Консоль] " + message.from_user.username + " использовал команду start [" + Date.get_date() + "]\n"
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
        # Подключаемся к базе данных sqlite
        conn = sqlite3.connect("db.db")
        # Создаём курсор
        cursor = conn.cursor()
        # Ищем пользователя у которого такой chat id
        cursor.execute(
            "SELECT * FROM users Where Chat_id = '" + str(message.chat.id) + "'"
        )
        # Выносим результат из базы
        user = cursor.fetchone()
        # None-Пользователя нет
        # Если пользователя нет то заносим его базу данных sqlite
        if user is None:
            cursor.execute(
                "UPDATE subscriptions SET subscriptions = subscriptions+1 WHERE Month = '" + Date.get_date_by_code(
                    "%m") + "'"
                )
            conn.commit()
            cursor.execute(
                "INSERT INTO users(Chat_Id,Username,first_name,last_name,Registration_date) VALUES ({0},'{1}',"
                "'{2}','{3}','{4}')".format(
                    message.chat.id,
                    message.from_user.username,
                    message.from_user.first_name,
                    message.from_user.last_name,
                    Date.get_date()
                )
                )
            conn.commit()
            write_log(
                "[База данных] Добавлен новый пользователь в базу данных [" + Date.get_date() + "]\n"
            )
            conn.close()


    @bot.message_handler(content_types=["text"])
    def main(message):
        # Если у пользователя нету имени то соединяем его имя и фамилию
        if message.from_user.username is None:
            message.from_user.username = (
                    message.from_user.first_name + "_" + message.from_user.last_name
            )
        # Смотрим что отослал пользователь
        if message.text == "Новости":
            # Выводим лог
            write_log(
                "[Консоль] " + message.from_user.username + " использовал кнопку новости [" + Date.get_date() + "]\n"
            )
            # Получем html главной страницы сайта point.md
            html = requests.get("https://point.md").text
            # Указываем что будем парсить и каким парсером
            # lxml-хороший быстрый парсер
            # html.parser - простой но позволяет работать со сломанными тэгами типо div></div
            try:
                parser = BeautifulSoup(html, "lxml")
            except FeatureNotFound:
                write_log(
                    "[Предупреждение] Парсер lxml не найден!Будет использован html.parser [" + Date.get_date() + "]\n"
                )
                parser = BeautifulSoup(html, "html.parser")
            # Создаём список куда будем класть все заголовки ссылки время статей
            posts = []
            # В цикле собираем все заголовки время и ссылки в массив
            for el in parser.select(".post-list-container-item"):
                title = el.select(".post-list-container-item-text-title > a")
                time = el.select(".post-list-time")
                links = [a["href"] for a in el.find_all("a", href=True) if a.text]
                posts.append(
                    {"title": title[0].text, "time": time[0].text, "href": links[0]}
                )
            # Также в цикле отсылаем сообщения с новостями
            for post in posts[0: int(global_iteration_news)]:
                bot.send_message(
                    message.chat.id,
                    post["title"]
                    + "\nВремя:" + post["time"]
                    + "\nСсылка:https://point.md/" + post["href"]
                )
        elif message.text == "Погода":
            # Выводим лог
            write_log(
                "[Консоль] " + message.from_user.username + " использовал кнопку Погода [" + Date.get_date() + "]\n"
            )
            msg = bot.send_message(message.chat.id, "Введи название города")
            bot.register_next_step_handler(msg, weather)
        elif message.text == "Школа":
            # Выводим лог
            write_log(
                "[Консоль] " + message.from_user.username + " использовал кнопку школа [" + Date.get_date() + "]\n"
            )
            msg_school = bot.send_message(
                message.chat.id,
                "Что вам нужно?:\n1)Калькулятор\n2)Быстрый поиск в вики\nВыбери нужный вариант и отошли мне",
            )
            bot.register_next_step_handler(msg_school, school)
        elif message.text == "Цитата":
            # Выводим лог
            write_log(
                "[Консоль] " + message.from_user.username + " использовал кнопку цитата [" + Date.get_date() + "]\n"
            )
            # Загружаем json
            with open("etc/quotes.json", encoding="utf-8") as f:
                quote = json.load(f)
            random_json = random.randint(0, 10266)
            msg = (
                    "Цитата:" + quote[random_json]["quote"]
                    + "\nАвтор:" + quote[random_json]["source"]
            )
            # Отсылаем цитату
            bot.send_message(message.chat.id, msg)
        elif message.text == admin_password:
            msg = bot.send_message(
                message.chat.id,
                """Добро пожаловать в администраторскую панель
Доступные опции:
1)Отослать сообщение во все чаты
2)Отослать сообщение определенному человеку""",
            )
            write_log(
                "[Админ панель] "
                + message.from_user.username +
                " зашёл в администраторскую  панель [" + Date.get_date() + "]\n"
            )
            bot.register_next_step_handler(msg, admin)
        else:
            bot.send_message(message.chat.id, "Ваш запрос не понятен")


    def admin(message):
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
            bot.send_message(
                message.chat.id, "Введите значения из предложенных"
            )


    # Первая функция смотрим chat id
    def admin_send_msg_step_1(message):
        global chat_id, who
        who = message.text
        connection = sqlite3.connect("db.db")
        cursor = connection.cursor()
        cursor.execute("SELECT Chat_id FROM users Where Username = '" + who + "'")
        chat_id = cursor.fetchone()
        if chat_id is not None:
            msg = bot.send_message(
                message.chat.id, "Какое сообщение вы хотите отослать"
            )
            bot.register_next_step_handler(msg, admin_send_msg_step_2)
        else:
            bot.send_message(message.chat.id, "Пользователь не найден")


    # Вторая функция отправляем сообщение
    def admin_send_msg_step_2(message):
        if message.from_user.username is None:
            message.from_user.username = "Неизвестный"
        msg = message.text
        bot.send_message(chat_id[0], msg)
        bot.send_message(message.chat.id, "Сообщение отправленно")
        write_log(
            "[Админ] "
            + message.from_user.username +
            " отравил сообщение "
            + msg +
            " пользователю "
            + who +
            " [" + Date.get_date() + "]\n"
        )


    # ------------
    # Функция для отсылки сообщений всем пользователем бота

    def admin_send_msg_to_all(message):

        admin_message = message.text
        write_log(
            "[Админ] " + admin_message + " [" + Date.get_date() + "]\n"
        )
        con = sqlite3.connect("db.db")
        cur = con.cursor()
        chat_ids = cur.execute("SELECT Chat_id FROM user")
        # И в цикле выводим  сообщение при старте в чаты
        for el in chat_ids:
            bot.send_message(el[0], admin_message)


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
            # Решаем уравнение но отключаем встроенные функции и типы языка
            answer = eval(msg, {"__builtins__": {}})
            bot.send_message(message.chat.id, answer)
        except SyntaxError:
            # Если ошибка отсылаем сообщение
            bot.send_message(message.chat.id, "Что то не так")


    def wiki(message):
        search = message.text
        # Ставим русскикй язык
        wikipedia.set_lang("ru")
        try:
            # Ищем в вики страницу которую запросили
            text = wikipedia.summary(search, sentences=5)
            # Отсылаем текст из вики пользователю
            bot.send_message(message.chat.id, text)
        except wikipedia.exceptions.PageError:
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
                "Город:" + town
                + "\nСтатус:" + w.detailed_status
                + "\nТемпература:" + str(temp["temp"]) + "°"
                + "\nОщущаеться как:" + str(temp["feels_like"]) + "°"
                + "\nСкорость ветра:" + str(wind["speed"]) + " м/с",
            )
        except exceptions.UnauthorizedError:
            write_log(
                "[Предупреждение] Запрос не был выполнен так как неправильный api ключ [" + Date.get_date() + "]\n"
            )
            bot.send_message(message.chat.id, "Произошла внутрения ошибка")
        except exceptions.NotFoundError:
            bot.send_message(message.chat.id, "Город не найден")


    bot.polling(none_stop=True)
else:
    print("Напишите значения из списка")