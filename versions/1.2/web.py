try:
    import functions
    import sys
    import config
    import traceback
    import sqlite3
    import matplotlib.pyplot as plt
    import numpy as np
    import telebot
    from flask import Flask, render_template, request
except ModuleNotFoundError:
    error = sys.exc_info()
    functions.write_log(
        "[Ошибка] Какой-то модуль не устоновлен!Перепроверьте список устоновленных модулей\nОшибка:"+str(error[1]),True
    )
    exit(1)

app = Flask(__name__)
bot = telebot.TeleBot(config.token)
app

@app.route("/", methods=["POST", "GET"])
def index():
    # Если метод запроса POST отдаём логи
    if request.method == "POST":
        # Открываем логи и держим их открытыми
        f = open("logs.txt")
        text = f.read()
        return text
    else:
        # Иначе рендерим страничку html
        return render_template("log.html", date=functions.get_date(), con=config)


@app.route("/statistics")
def statistics():
    # Создаём график
    fig = plt.figure()
    # Добавляем оси
    ax = fig.add_subplot(111)
    if config.sqlite == True:
        # Подключаем sqlite
        con = sqlite3.connect("db.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM subscriptions")
        row = cur.fetchall()
    else:
        config.cur.execute("SELECT * FROM subscriptions")
        row = config.cur.fetchall()
    subscriptions = []
    for el in row:
        subscriptions.append(el[1])
    ax.set_xlabel("Месяца")
    ax.set_ylabel("Подписчики")
    ax.plot([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], subscriptions)
    fig.savefig("static/plot.png")
    return render_template("statistics.html", date=functions.get_date())


@app.route("/database", methods=["GET", "POST"])
def db():
    action = request.args.get("action")
    if request.method == "GET":
        if action == "main":
            if config.sqlite == True:
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
                row = cur.fetchall()
                db_system = "sqlite"
                db = "Main"
            else:
                config.cur.execute(
                    "SELECT table_name FROM information_schema.tables where table_schema='"
                    + config.mysql_db
                    + "'"
                )
                row = config.cur.fetchall()
                db_system = "mysql"
                db = config.mysql_db
            return render_template(
                "database.html",
                date=functions.get_date(),
                data=row,
                action=action,
                db_system=db_system,
                db=db,
            )
        elif action == "sql_query":
            return render_template("database.html", action=action)
        else:
            if config.sqlite == True:
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                # Получаем данные с таблице(sqlite)
                cur.execute("SELECT * FROM " + action)
                data = cur.fetchall()
                # Получаем имена столбцов
                cur.execute("PRAGMA table_info(" + action + ")")
                column_names = cur.fetchall()
                db_system = "sqlite"
            else:
                # Получаем данные с таблице(mysql)
                config.cur.execute("SELECT * FROM " + action)
                data = config.cur.fetchall()
                # Получаем имена столбцов
                config.cur.execute(
                    "select column_name from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='" + action + "'"
                )
                column_names = config.cur.fetchall()
                db_system = "mysql"
            return render_template(
                "database.html",
                date=functions.get_date(),
                data=data,
                action=action,
                column_names=column_names,
                db_system=db_system,
            )
    else:
        # Смотрим что дали
        sql = request.form.get("sql")
        if config.sqlite == True:
            # Выполняем запрос на sqlite
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            cur.execute(sql)
            # Потверждаем изменения
            con.commit()
        else:
            # Выполняем запрос на mysql
            config.cur.execute(sql)
            # Потверждаем изменения
            config.con.commit()
        return render_template(
            "database.html",
            date=functions.get_date(),
            data="Success",
            action="sql_query",
        )


@app.route("/admin_panel", methods=["GET", "POST"])
def admin_panel():
    action = request.args.get("action")
    if request.method == "GET":
        if action == "main":
            return render_template(
                "admin_panel.html", date=functions.get_date(), action=action
            )
        else:
            return render_template(
                "admin_panel.html", date=functions.get_date(), action=action
            )
    else:
        msg_to_all = request.form.get("msg_to_all")
        nicname = request.form.get("nicname")
        msg = request.form.get("msg")
        type_form = request.form.get("type_form")
        if type_form == "send_message_to_all":
            if msg_to_all == "":
                return render_template(
                    "admin_panel.html",
                    date=functions.get_date(),
                    action="main",
                    data="Заполните форму",
                )
            else:
                if config.sqlite == True:
                    con = sqlite3.connect("db.db")
                    cur = con.cursor()
                    cur.execute("SELECT Chat_id FROM users")
                    rows = cur.fetchall()
                    for row in rows:
                        bot.send_message(row[0], msg_to_all)
                    con.close()
                else:
                    config.cur.execute("SELECT Chat_Id FROM `user_subscriptions`")
                    rows = config.cur.fetchall()
                    for row in rows:
                        bot.send_message(row[0], msg_to_all)
                return render_template(
                    "admin_panel.html",
                    date=functions.get_date(),
                    action="main",
                    data="Успех",
                )
        else:
            if nicname == "" and msg == "" or nicname == "" or msg == "":
                return render_template(
                    "admin_panel.html",
                    date=functions.get_date(),
                    action="main",
                    data="Заполните форму",
                )
            else:
                if config.sqlite == True:
                    con = sqlite3.connect("db.db")
                    cur = con.cursor()
                    cur.execute(
                        "SELECT Chat_id FROM users WHERE Username = '" + nicname + "'"
                    )
                    row = cur.fetchall()
                    len_row = len(row)
                    if len_row == 0:
                        return render_template(
                            "admin_panel.html",
                            date=functions.get_date(),
                            action="main",
                            data="Пользователь не найден",
                        )
                    else:
                        bot.send_message(row[0][0], msg)
                        con.close()
                else:
                    config.cur.execute(
                        "SELECT Chat_Id FROM `user_subscriptions` WHERE Username = '" + nicname + "'"
                    )
                    row = config.cur.fetchall()
                    bot.send_message(row[0][0], msg)
                return render_template(
                    "admin_panel.html",
                    date=functions.get_date(),
                    action="main",
                    data="Успех",
                )


@app.route("/settings", methods=["GET", "POST"])
def settings():
    # Если есть запрос типа POST
    if request.method == "POST":
        # Читаем данные из формы
        telegram_token = request.form.get("telegram_token")
        owm_token = request.form.get("owm_token")
        start_msg = request.form.get("start_msg")
        global_iteration_news = request.form.get("iteration_news")
        admin_panel_password = request.form.get("admin_panel_password")
        sqlite = request.form.get("Sqlite")
        log_reading_frequency = request.form.get("log_reading_frequency")
        mysql_user = request.form.get("mysql_user")
        mysql_password = request.form.get("mysql_password")
        mysql_db = request.form.get("mysql_db")
        # Если данные mysql не указаны то присваеваем значения им из конфига
        if mysql_user == None and mysql_password == None and mysql_db == None:
            mysql_user = config.mysql_user
            mysql_password = config.mysql_password
            mysql_db = config.mysql_db
        # Создаём новый конфиг
        new_config = (
            """import functions
from datetime import datetime
#Из модуля pyowm utils получаем функцию для получения стандартного конфига
from pyowm.utils.config import get_default_config
#Токен взятый с @BotFather
token = '"""+ telegram_token + """'
#Токен взятый с сайта openweathermap.org
weather_token = '""" + owm_token + """'
#Получаем стандартный конфиг для pyowm
config_dict = get_default_config()
#Устонавливаем русский язык в этом конфиге
config_dict['language'] = 'ru'
#Сообщение при старте
on_start_msg = '""" + start_msg + """'
#Сколько показывать новостей
global_iteration_news = """  + global_iteration_news  + """
#Секретный ключ для входа в админ панель
admin_password = '""" + admin_panel_password + """'
#Частота чтения логов
log_reading_frequency = """ + log_reading_frequency + """
#База данных sqlite
sqlite=""" + sqlite  + """
#Пользователь к базе данных mysql
mysql_user = '""" + mysql_user + """'
#Пароль к пользователю mysql
mysql_password = '""" + mysql_password + """'
#База данных mysql
mysql_db = '""" + mysql_db + """'
if sqlite==False:
	import pymysql
	#Подключаемся к базе данных
	try:
		con = pymysql.connect('localhost', mysql_user, mysql_password, mysql_db)
	except pymysql.err.OperationalError:
		functions.write_log('''[Ошибка] Невозможно подключиться к базе данных!Проверьте правильность данных для подключенния ['''+str(datetime.now())+''']
''')
		exit(1)
	#Создаём курсор.Курсор нужен для выполнений операций с базой данных
	cur = con.cursor()
		"""
        )
        # Пишем в файл
        functions.file(new_config, "config.py", "text", "w")
        return render_template(
            "settings.html", con=config, date=functions.get_date(), msg="Успех"
        )

    else:
        return render_template("settings.html", con=config, date=functions.get_date())


@app.route("/information")
def information():
    # Получаем версию python
    version_python = str(sys.version_info.major) + "." + str(sys.version_info.minor)
    if config.sqlite == True:
        db = "sqlite"
    else:
        db = "mysql"
    return render_template(
        "information.html",
        date=functions.get_date(),
        version_python=version_python,
        db=db,
    )
if __name__ == '__main__':
    app.run(debug = False)
