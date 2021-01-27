try:
    from lib import write_log, get_all_versions, check_admin, Date, get_collection, generate_string
    import sys
    import config
    import telebot
    from flask import Flask, render_template, request, flash, make_response, redirect
    import hashlib
    from uuid import uuid4
    from pymongo import MongoClient
    from pymongo.errors import OperationFailure
except ModuleNotFoundError:
    error = sys.exc_info()
    write_log(
        """[Ошибка] Какой-то модуль не устоновлен!Перепроверьте список устоновленных модулей
Ошибка:""" + str(error[1]) + "\n", True
    )
    exit(1)

app = Flask(__name__)
bot = telebot.TeleBot(config.token)
Date = Date()


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html", admin=check_admin(request.cookies.get('token')))
    else:
        admin_login = request.form.get("login")
        admin_password = request.form.get("password")
        hash_password = hashlib.md5(admin_password.encode())
        admin = config.admins.find_one({"login": admin_login})
        if admin_login == admin["login"] and hash_password.hexdigest() == admin["password"]:
            hash_admin = uuid4()
            config.admins.update_one({"login": admin_login}, {"$set": {"auth_token": str(hash_admin)}})
            resp = make_response(
                redirect("http://127.0.0.1:5000/admin_panel?action=main")
            )
            resp.set_cookie('token', str(hash_admin), max_age=31536000, samesite='Lax')
            return resp
        else:
            return render_template('login.html',
                                   msg="Неправильный логин или пароль",
                                   admin=check_admin(request.cookies.get('token'))
                                   )


@app.route("/")
def index():
    versions = get_all_versions()
    # Иначе рендерим страничку html
    return render_template("index.html",
                           log_reading_frequency=config.log_reading_frequency,
                           admin=check_admin(request.cookies.get('token')),
                           versions=versions,
                           )


@app.route("/log", methods=["POST", "GET"])
def log():
    # Если метод запроса POST отдаём логи
    if request.method == "POST":
        # Читаем логи
        f = open("logs.txt")
        text = f.read()
        f.close()
        return text
    else:
        # Иначе рендерим страничку html
        return render_template("log.html",
                               log_reading_frequency=config.log_reading_frequency,
                               admin=check_admin(request.cookies.get('token'))
                               )


@app.route("/database", methods=["GET", "POST"])
def db():
    action = request.args.get("action")
    if request.method == "GET":
        if action == "main":
            data = config.db.list_collection_names()
            return render_template(
                "database.html",
                data=data,
                action=action,
                admin=check_admin(request.cookies.get('token'))
            )
        elif action == "sql_query":
            return render_template("database.html",
                                   action=action,
                                   admin=check_admin(request.cookies.get('token'))
                                   )
        else:
            collection = get_collection(action)
            return render_template(
                "database.html",
                action=action,
                collection=collection,
                admin=check_admin(request.cookies.get('token'))
            )
    else:
        try:
            db.command(request.form.get("query"))
        except OperationFailure:
            return render_template(
                "database.html",
                msg="Ошибка",
                action="sql_query",
                admin=check_admin(request.cookies.get('token'))
            )
        return render_template(
            "database.html",
            msg="Успех",
            action="sql_query",
            admin=check_admin(request.cookies.get('token'))
        )


@app.route("/admin_panel", methods=["GET", "POST"])
def admin_panel():
    action = request.args.get("action")
    if request.method == "GET":
        if action == "main":
            return render_template(
                "admin_panel.html",
                action="main",
                admin=check_admin(request.cookies.get('token'))
            )
        elif action == "logout":
            res = make_response(
                render_template("login.html",
                                admin=check_admin(request.cookies.get('token'))
                                )
            )
            res.set_cookie('token', max_age=0)
            return res
        else:
            return render_template(
                "admin_panel.html",
                action=action,
                admin=check_admin(request.cookies.get('token'))
            )
    else:
        msg_to_all = request.form.get("msg_to_all")
        nickname = request.form.get("nickname")
        msg = request.form.get("msg")
        type_form = request.form.get("type_form")
        if type_form == "send_message_to_all":
            if msg_to_all == "":
                return render_template(
                    "admin_panel.html",
                    action="send_message_to_all",
                    msg="Заполните форму",
                    admin=check_admin(request.cookies.get('token'))
                )
            else:
                for element in config.users.find():
                    bot.send_message(element['chat_id'], msg_to_all)
                return render_template(
                    "admin_panel.html",
                    action="send_message_to_all",
                    msg="Успех",
                    admin=check_admin(request.cookies.get('token'))
                )
        else:
            if nickname != "" and msg != "":
                user = config.users.find_one({"username": nickname})
                if user is None:
                    return render_template(
                        "admin_panel.html",
                        action="send_message_to_user",
                        msg="Пользователь не найден",
                        admin=check_admin(request.cookies.get('token'))
                    )
                else:
                    bot.send_message(user['chat_id'], msg)
                    return render_template(
                        "admin_panel.html",
                        action="send_message_to_user",
                        msg="Успех",
                        admin=check_admin(request.cookies.get('token'))
                    )
            else:
                return render_template(
                    "admin_panel.html",
                    action="send_message_to_user",
                    msg="Заполните форму",
                    admin=check_admin(request.cookies.get('token'))
                )


@app.route("/settings", methods=["GET", "POST"])
def settings():
    config_elements = {
        'token': config.token,
        'weather_token': config.weather_token,
        'on_start_msg': config.on_start_msg,
        'global_iteration_news': config.global_iteration_news,
        'admin_password': config.admin_password,
        'log_reading_frequency': config.log_reading_frequency,
    }
    # Если есть запрос типа POST
    if request.method == "POST":
        # Читаем данные из формы
        config_elements['token'] = telegram_token = request.form.get("telegram_token")
        config_elements['weather_token'] = owm_token = request.form.get("owm_token")
        config_elements['on_start_msg'] = start_msg = request.form.get("start_msg")
        config_elements['global_iteration_news'] = global_iteration_news = request.form.get("iteration_news")
        config_elements['admin_password'] = admin_panel_password = request.form.get("admin_panel_password")
        config_elements['log_reading_frequency'] = log_reading_frequency = request.form.get("log_reading_frequency")
        # Создаём новый конфиг
        new_config = (
                """from pymongo import MongoClient
from lib import write_log, Date
# Из модуля pyowm utils получаем функцию для получения стандартного конфига
from pyowm.utils.config import get_default_config

# Соединяемся с базой данных
client = MongoClient('localhost', 27017)
db = client.Telegram
users = db.users
admins = db.admins
# Токен взятый с @BotFather
token = '""" + telegram_token + """'
# Токен взятый с сайта openweathermap.org
weather_token = '""" + owm_token + """'
# Получаем стандартный конфиг для pyowm
config_dict = get_default_config()
# Устонавливаем русский язык в этом конфиге
config_dict['language'] = 'ru'
# Сообщение при старте
on_start_msg = '""" + start_msg + """'
# Сколько показывать новостей
global_iteration_news = """ + global_iteration_news + """
# Секретный ключ для входа в админ панель
admin_password = '""" + admin_panel_password + """'
# Частота чтения логов
log_reading_frequency = """ + log_reading_frequency + """
"""
        )
        # Пишем в файл
        with open("config.py", "w", encoding="utf-8") as f:
            f.write(new_config)
        return render_template(
            "settings.html",
            con=config_elements,
            msg="Успех",
            admin=check_admin(request.cookies.get('token'))
        )

    else:
        return render_template("settings.html",
                               con=config_elements,
                               admin=check_admin(request.cookies.get('token'))
                               )


@app.route("/information")
def information():
    # Получаем версию python
    version_python = str(sys.version_info.major) + "." + str(sys.version_info.minor)
    versions = get_all_versions()
    return render_template(
        "information.html",
        version_python=version_python,
        version_bot=versions[-1]['version'],
        date_update=versions[-1]['date_update'],
        description_update=versions[-1]['description_update'],
        admin=check_admin(request.cookies.get('token'))
    )


@app.route("/chat", methods=["GET", "POST"])
def chat():
    admin = check_admin(request.cookies.get('token'))
    messages = config.chat.find()
    if request.method == "GET":
        return render_template("chat.html",
                               admin=admin,
                               messages=messages
                               )
    else:
        message = request.form.get("form_message")
        config.chat.insert_one({
            "_id": generate_string(10),
            "login": admin[1]['login'],
            "message": message,
            "date": Date.get_date()
        })
        return render_template("chat.html",
                               admin=admin,
                               messages=messages
                               )


if __name__ == '__main__':
    app.run(debug=True)
