from pymongo import MongoClient
import time
import xml.etree.ElementTree
import random
import string

# Соединяемся с базой данных
client = MongoClient('localhost', 27017)
db = client.Telegram
admins = db.admins

class Color:
    purple = '\033[95m'
    cyan = '\033[96m'
    dark_cyan = '\033[36m'
    blue = '\033[94m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    bold = '\033[1m'
    underline = '\033[4m'
    end = '\033[0m'


class Date:
    def __init__(self):
        self.seconds = time.time()
        self.date = time.localtime(self.seconds)

    def get_date(self):
        # Преоброзуем в стандартный вариант
        now = time.strftime("%d/%m/%Y %H:%M", self.date)
        return now

    def get_seconds(self):
        return int(self.seconds)

    def get_date_by_code(self, date_code):
        # Преоброзуем в вариант который запросили
        now = time.strftime(date_code, self.date)
        return now


def generate_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    rand_string = ''.join(random.sample(letters_and_digits, length))
    return rand_string

def check_admin(token):
    if token is not None:
        admin_db = admins.find_one({"auth_token": token})
        if admin_db is None:
            return None
        else:
            return True, admin_db
    else:
        return None


def get_collection(name_collection):
    data = db.command({
        "find": name_collection,
    })
    if not data['cursor']['firstBatch']:
        return None
    else:
        values = []
        keys = data['cursor']['firstBatch'][0].keys()
        for i in range(0, len(data['cursor']['firstBatch'])):
            values.append(list(data['cursor']['firstBatch'][i].items()))
        return values



def get_all_versions():
    tree = xml.etree.ElementTree.parse("etc/updates.xml")
    updates = tree.find('updates')
    updates_list = []
    for el in updates.findall('update'):
        version = el.attrib['version']
        description_update = el.find('description_update').text.replace("\t", "")
        date_update = el.find('date_update').text
        updates_list.append({
            'version': version,
            'date_update': date_update,
            'description_update': description_update
        })
    return updates_list


def write_log(log, literals_in_console=False):
    # Если нужны литералы то выводим лог вместе с ними
    if literals_in_console:
        print(log)
    # Если не нужны литералы убираем их
    else:
        console_log = log.replace("\n", "")
        print(console_log)
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(log)
