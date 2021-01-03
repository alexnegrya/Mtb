import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup as BS


def get_date():
    # Получаем дату
    date = datetime.now()
    # И преоброзуем в нужный вариант
    now = date.strftime("%m/%d/%Y %H:%M")
    return now


def get_html(url):
    response = requests.get(url)
    return response.text


def file(data, file, t, method):
    with open(file, method, encoding="utf-8") as f:
        if t == "json" and method == "a" or method == "w":
            json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        elif t == "json" and method == "r":
            return json.load(f)
        elif t == "text" and method == "r":
            return f.read()
        else:
            f.write(data)
            return True


def write_log(log):
    console_log = log.replace("\n", "")
    print(console_log)
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(log)
