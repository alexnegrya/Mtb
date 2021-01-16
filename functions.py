import time

def get_date(date_code="%d/%m/%Y %H:%M"):
	#Если код даты не изменился даём полную дату
	if date_code == "%d/%m/%Y %H:%M":
	    # Получаем дату
	    seconds = time.time()
	    date = time.localtime(seconds)
	    # И преоброзуем в нужный вариант
	    now = time.strftime(date_code,date)
	    return now
	#Если код даты дали другой 
	else:
		#То Получаем дату
	    seconds = time.time()
	    date = time.localtime(seconds)
	    # И преоброзуем в вариант который запросили
	    now = time.strftime(date_code,date)
	    return now

def write_log(log,literals_in_console=False):
	#Если нужны литералы то выводим лог вместе с ними
    if literals_in_console:
        print(log)
    #Если не нужны литералы убираем их
    else:
        console_log = log.replace("\n", "")
        print(console_log)
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(log)

