try:
    import sys
    from lib import Date,  write_log, get_all_versions, Color, generate_string
    import json
    import telebot
    import requests
    import config
    import pyowm
    from pyowm.commons.exceptions import UnauthorizedError, NotFoundError
    import wikipedia
    import signal
    import random
    from bs4 import FeatureNotFound, BeautifulSoup
    from telebot import types
except ModuleNotFoundError:
    error = sys.exc_info()
    write_log(
        """[Ошибка] Какой-то модуль не устоновлен!Перепроверьте список устоновленных модулей!
[Ошибка] Ошибка:""" + str(error[1]) + "\n", True
    )
    exit(1)

# Убираем вывод ошибке о прерывание
signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))
# Инциализация бота
bot = telebot.TeleBot(config.token)
owm = pyowm.OWM(config.weather_token, config.config_dict)
# Создаём экземпляры классов
Date = Date()
Color = Color()
# Получаем все версии бота
versions = get_all_versions()

print("""
.___  ___. .___________..______   
|   \/   | |           ||   _  \  
|  \  /  | `---|  |----`|  |_)  | 
|  |\/|  |     |  |     |   _  <  
|  |  |  |     |  |     |  |_)  | 
|__|  |__|     |__|     |______/ 
""")
print(
    """Добро пожаловать в mtb бота версии """ + versions[-1]['version'] + """
Чтобы начать запуск бота напишите 'Запуск' или напишите 'Настройки' для входа в настройки бота"""
)
options = input(":" + Color.green)

if options == "Настройки":
    print(
        """{} Вы вошли в настройки,чтобы изменить какие-то значения используйте config.переменная = 'ваше значение'.
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
Измения будут приняты ТОЛЬКО для этого запуска
Напишите Выход чтобы выйти из настроек и запустить бота""".format(Color.end)
    )
    while True:
        cmd = input(":")
        if cmd == "Выход":
            options = "Запуск"
            break
        else:
            exec(cmd)
            print("Конфигурационный файл изменён")
if options == "Запуск":
    # Смотрим если есть сообщение при старте
    if config.on_start_msg != "":
        for element in config.users.find():
            bot.send_message(element['chat_id'], config.on_start_msg)
    # Выводим лог
    write_log(
        Color.end+"[Консоль] Бот запущен и работает [" + Date.get_date() + "]\n"
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
        user = config.users.find_one({"chat_id": message.chat.id})
        if user is None:
            config.users.insert_one({
                "_id": generate_string(10),
                "chat_id": message.chat.id,
                "username": message.from_user.username,
                "first_name": message.from_user.first_name,
                "last_name": message.from_user.last_name,
                "Registration_date": Date.get_date()
            })
            write_log(
                "[База данных] Добавлен новый пользователь в базу данных [" + Date.get_date() + "]\n"
            )

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
            html = requests.get("https://point.md/ru/novosti/?date_to="
                                + str(Date.get_seconds()) + "&count=" + str(config.global_iteration_news)).text
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
            # В цикле собираем все заголовки время и ссылки в массив
            for el in parser.select(".post-list-container-item"):
                title = el.select(".post-list-container-item-text-title > a")
                time = el.select(".post-list-time")
                links = [a["href"] for a in el.find_all("a", href=True) if a.text]
                bot.send_message(
                    message.chat.id,
                    title[0].text
                    + "\nВремя:" + time[0].text
                    + "\nСсылка:https://point.md/" + links[0]
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
                """Что вам нужно?:
1)Калькулятор
2)Быстрый поиск в вики
Выбери нужный вариант и отошли мне""",
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
        elif message.text == config.admin_password:
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
        whom = message.text
        user = config.users.find_one({"username": whom})
        print(user)
        if user is not None:
            msg = bot.send_message(
                message.chat.id, "Какое сообщение вы хотите отослать"
            )
            bot.register_next_step_handler(msg, admin_send_msg_step_2, user['chat_id'], whom)
        else:
            bot.send_message(message.chat.id, "Пользователь не найден")

    # Вторая функция отправляем сообщение
    def admin_send_msg_step_2(message, chat_id, whom):
        if message.from_user.username is None:
            message.from_user.username = (
                    message.from_user.first_name + "_" + message.from_user.last_name
            )
        msg = message.text
        from_admin = message.from_user.username
        bot.send_message(chat_id, msg, whom)
        bot.send_message(message.chat.id, "Сообщение отправленно")
        write_log(
            "[Админ] "+from_admin+" отравил "+msg+" пользователю "+whom+" [" + Date.get_date() + "]\n"
        )

    # Функция для отсылки сообщений всем пользователем бота
    def admin_send_msg_to_all(message):
        admin_message = message.text
        for user in config.users.find():
            bot.send_message(user['chat_id'], admin_message)
        write_log(
            "[Админ] " + admin_message + " [" + Date.get_date() + "]\n"
        )


    def school(message):
        text = message.text
        if text == "1":
            msg = bot.send_message(message.chat.id, "Введи числа:")
            bot.register_next_step_handler(msg, calculator)
        elif text == "2":
            msg = bot.send_message(message.chat.id, "Что найти в вики?:")
            bot.register_next_step_handler(msg, wiki)
        else:
            bot.send_message(message.chat.id, "Введи то что указано в списки!")


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
        except UnauthorizedError:
            write_log(
                "[Предупреждение] Запрос не был выполнен так как неправильный api ключ [" + Date.get_date() + "]\n"
            )
            bot.send_message(message.chat.id, "Произошла внутрения ошибка")
        except NotFoundError:
            bot.send_message(message.chat.id, "Город не найден")


    bot.polling(none_stop=True)
else:
    print("Напишите значения из списка")