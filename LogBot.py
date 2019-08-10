import os
import io
import re
from itertools import islice
import configparser
from slacker import Slacker

#Читаем файл конфигурации и заполняем константы:
config = configparser.ConfigParser()
try:
    config.read('config.ini')
    file_name = config['DEFAULT']['FileName']
    cur_dir = config['DEFAULT']['CurrentDirectory']
    temp_file_name = config['DEFAULT']['TempFile']
    slack_tokken = config['DEFAULT']['SlackTokken']
except Exception as ex:
    print('Ошибка при чтении конфига: ' + str(ex))

#Читаем временный файл с номером строки последнего цикла мониторинга
try:
    with io.open(temp_file_name, encoding='utf-8') as temp:
        last_line_num = int(temp.readline())
        print('Временный файл существует, число равно: ' + str(last_line_num))
except Exception:
    last_line_num = 0
    print('Временный файл отсутствует, число равно: ' + str(last_line_num))

#Заводим переменные
slack = Slacker(slack_tokken)
errors = list()
currentError = None
last_line_num_temp = 0

def findLastline():
    try:
        with io.open(cur_dir + file_name, encoding='utf-8') as file_temp:
            return len(file_temp.readlines())
    except Exception as ex:
        print('Ошибка при первичном чтении: ' + str(ex))

#Читаем лог файл с последней строки, на которой остановились
try:
    with io.open(cur_dir + file_name, encoding='utf-8') as file:
        lastline = findLastline()
        if lastline == last_line_num + 1:
            print('Изменений в файле нет')
        else:
            for num, line in enumerate(islice(file, last_line_num, None), last_line_num):
                if not re.match(r'[0-9]{4}\-[0-9]{2}\-[0-9]{2} [0-9]{2}\:[0-9]{2}\:[0-9]{2}\.[0-9]{4}\|.*\|.*$', line):
                    currentError = str(currentError) + str(num + 1) + ': ' + line
                    if num + 1 == lastline:
                        errors.append(currentError)
                else:
                    if currentError is not None:
                        errors.append(currentError)
                    currentError = str(num + 1) + ': ' + line
                last_line_num_temp = num
            #Пишем во временный файл номер строки, на которой закончили мониторинг
            try: 
                with io.open(temp_file_name, 'w', encoding='utf-8') as temp:
                    temp.write(str(last_line_num_temp))
            except Exception as ex:
                print('Ошибка при записи числа в файл: ' + str(ex))

            #Отправим последнюю ошибку в чатик
            try:
                for i in range(len(errors)):
                    currentError = currentError + errors[i]
                print(currentError)
                #slack.chat.post_message('#uismv_logs', currentError)
            except Exception as ex:
                print('Ошибка при отправке в чат: ' + str(ex))
except Exception as ex:
    print('Ошибка при вычислении массива: ' + str(ex))