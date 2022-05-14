import traceback

import requests
import telebot
import os
import time
import json
import ast
import re
import schedule
from datetime import datetime
from time import sleep
from ntoken import TOKEN
from config import dest_cameras, dest_schemes, dest_ZOOM, url, login, password, vmix_ip_dict
from DB import Files, Schemes, ZOOM
from schedule import start_date_every_day, start_date_smena_1, start_date_smena_2, start_date_smena_3, start_date_smena_4
from telebot import types
from apscheduler.schedulers.background import BackgroundScheduler

bot = telebot.TeleBot(TOKEN)

argument = 'main'

SchemesV = Schemes
FilesV = Files
ZOOMV = ZOOM

f = open("DB.py", "r")
db_data = f.read()
f.close()

smena_1 = ast.literal_eval(db_data.splitlines()[3])
smena_2 = ast.literal_eval(db_data.splitlines()[4])
smena_3 = ast.literal_eval(db_data.splitlines()[5])
smena_4 = ast.literal_eval(db_data.splitlines()[6])
every_day = ast.literal_eval(db_data.splitlines()[7])

commands_for_buttons = {'otpuska': 'Отпуска', 'ip_adr': 'ip', 'asb3bank': 'asb3bank', 'schemes_list': 'Схемы',
                        'cameras_list': 'Камеры', 'zoom_list': 'Zoom', 'journal': 'Журнал'}
commands_string = ''.join('{}{}'.format(key, val) for key, val in commands_for_buttons.items())

streaming_message_id = ""
vmix_ip = ""
stream_autorun = False
stream_stop = False

def create_keyboard(chatid):
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    buttons = [types.InlineKeyboardButton(text=commands_for_buttons[key], callback_data=key)
               for key in commands_for_buttons.keys()]

    keyboard.add(*buttons)

    add_button = types.InlineKeyboardButton(text='Добавить', callback_data='add, main')
    delete_button = types.InlineKeyboardButton(text='Удалить', callback_data='delete, main')
    if chatid == 147314671 or 1019904124:

        keyboard.add(add_button, delete_button)
    return keyboard


def cameras_send(cam_file, chatid, messageid):
    img = open(dest_cameras + Files.get(cam_file), 'rb')
    bot.send_photo(chatid, img)
    keyboard = types.InlineKeyboardMarkup()

    add_button = types.InlineKeyboardButton(text='Добавить', callback_data='add, cameras')
    delete_button = types.InlineKeyboardButton(text='Удалить', callback_data='delete, cameras_list')


    back_button = types.InlineKeyboardButton(text='Назад', callback_data='back')
    buttons = [types.InlineKeyboardButton(text=key, callback_data=key)
               for key in Files.keys()]
    keyboard.add(*buttons)
    if chatid == 147314671 or 1019904124:
        keyboard.add(add_button, delete_button)
    keyboard.add(back_button)
    bot.delete_message(chatid, messageid)
    bot.send_message(chatid, text='Выберите программу:', reply_markup=keyboard)


def schemes_send(scheme_file, chatid, messageid):
    doc = open(dest_schemes + Schemes.get(scheme_file), 'rb')
    bot.send_document(chatid, doc)
    keyboard = types.InlineKeyboardMarkup()

    add_button = types.InlineKeyboardButton(text='Добавить', callback_data='add, schemes')
    delete_button = types.InlineKeyboardButton(text='Удалить', callback_data='delete, schemes')

    back_button = types.InlineKeyboardButton(text='Назад', callback_data='back')

    buttons = [types.InlineKeyboardButton(text=key, callback_data=key)
               for key in Schemes.keys()]
    keyboard.add(*buttons)
    if chatid == 147314671 or 1019904124:
        keyboard.add(add_button, delete_button)
    keyboard.add(back_button)
    bot.delete_message(chatid, messageid)
    bot.send_message(chatid, text='Выбери схему:', reply_markup=keyboard)


def zoom_send(zoom_file, chatid, messageid):
    img = open(dest_ZOOM + ZOOM.get(zoom_file), 'rb')
    bot.send_photo(chatid, img)
    keyboard = types.InlineKeyboardMarkup()

    add_button = types.InlineKeyboardButton(text='Добавить', callback_data='add, zoom')
    delete_button = types.InlineKeyboardButton(text='Удалить', callback_data='delete, zoom')

    back_button = types.InlineKeyboardButton(text='Назад', callback_data='back')
    buttons = [types.InlineKeyboardButton(text=key, callback_data=key)
               for key in ZOOM.keys()]
    keyboard.add(*buttons)
    if chatid == 147314671 or 1019904124:
        keyboard.add(add_button, delete_button)
    keyboard.add(back_button)
    bot.delete_message(chatid, messageid)
    bot.send_message(chatid, text='Выбери тип трансляции:', reply_markup=keyboard)


@bot.message_handler(commands=['start'])
def start_message(message):

    chatid = message.chat.id
    keyboard = create_keyboard(chatid)
    bot.send_message(message.chat.id, 'Привет! Данные ... надо бы обновить', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: 'chatid' in call.data)
def chat_id(callback_query):
    chatid = callback_query.message.chat.id
    bot.send_message(chatid, chatid)


@bot.message_handler(commands=['journal'])
def journal(chatid, messageid):
    keyboard = types.InlineKeyboardMarkup()
    bot.delete_message(chatid, messageid)
    back_button = types.InlineKeyboardButton(text='Назад', callback_data='back')

    one_day_button = types.InlineKeyboardButton(text='Каждый день', callback_data='subscribe every_day')
    smena_1_button = types.InlineKeyboardButton(text='Рославцев и Сидоренко', callback_data='subscribe smena_1')
    smena_2_button = types.InlineKeyboardButton(text='Литвиненко и Мех', callback_data='subscribe smena_2')
    smena_3_button = types.InlineKeyboardButton(text='Астахов и Козлов', callback_data='subscribe smena_3')
    smena_4_button = types.InlineKeyboardButton(text='Бороздин и Долгов', callback_data='subscribe smena_4')
    unsubscribe_button = types.InlineKeyboardButton(text="Отписаться", callback_data="cancel")

    keyboard.add(smena_1_button, smena_2_button, smena_3_button, smena_4_button, one_day_button, unsubscribe_button)
    keyboard.add(back_button)
    bot.send_message(chatid, "Выберите тип рассылки:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: 'subscribe' in call.data)
def add_subscriber(callback_query):
    sub_type = callback_query.data[-10:]

    keyboard = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton(text='Назад', callback_data='back')
    unsubscribe_button = types.InlineKeyboardButton(text="Отписаться", callback_data="cancel")
    keyboard.add(unsubscribe_button, back_button)

    if "every_day" in sub_type and callback_query.message.chat.id not in every_day:
        every_day.append(callback_query.message.chat.id)
        bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                              text="Рассылка на каждый день добавлена", reply_markup=keyboard)
    elif "smena_1" in sub_type and callback_query.message.chat.id not in smena_1:
        smena_1.append(callback_query.message.chat.id)
        bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                              text="Рассылка Рославцев и Сидоренко добавлена", reply_markup=keyboard)
    elif "smena_2" in sub_type and callback_query.message.chat.id not in smena_2:
        smena_2.append(callback_query.message.chat.id)
        bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                              text="Рассылка Литвиненко и Мех добавлена", reply_markup=keyboard)
    elif "smena_3" in sub_type and callback_query.message.chat.id not in smena_3:
        smena_3.append(callback_query.message.chat.id)
        bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                              text="Рассылка Астахов и Козлов добавлена", reply_markup=keyboard)
    elif "smena_4" in sub_type and callback_query.message.chat.id not in smena_4:
        smena_4.append(callback_query.message.chat.id)
        bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                              text="Рассылка Бороздин и Долговв добавлена", reply_markup=keyboard)

    save_values()


@bot.callback_query_handler(func=lambda call: 'cancel' in call.data)
def unsubscribe(callback_query):
    chat_id = callback_query.message.chat.id

    keyboard = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton(text='Назад', callback_data='back')
    keyboard.add(back_button)

    if chat_id in smena_1:
        smena_1.remove(chat_id)
    elif chat_id in smena_2:
        smena_2.remove(chat_id)
    elif chat_id in smena_3:
        smena_3.remove(chat_id)
    elif chat_id in smena_4:
        smena_4.remove(chat_id)
    elif chat_id in every_day:
        every_day.remove(chat_id)

    bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                          text="Рассылка отменена", reply_markup=keyboard)

    save_values()


@bot.message_handler(content_types=["text"])
def manage_vmix(message):
    global streaming_message_id
    global vmix_number
    global vmix_ip
    global stream_autorun

    if "vmix" in message.text:                  # Отлавливаем сообщение-команду "vmix"+"номер"(+"старт")
        vmix_number = message.text[4]
        vmix_ip = get_vmix_ip(vmix_number)

        if not vmix_ip:
            bot.send_message(message.chat.id, "Vmix "+vmix_number+" недоступен")

        streaming_message_id = str(message.message_id + 1)                  # id сообщения с данными стрима

        """if "stop" in message.text:

            stop_stream(vmix_ip)
            bot.send_message(message.chat.id, "Потоки на Vmix"+vmix_number+" остановлены")

            return None"""

        if "start" in message.text:
            stream_autorun = True

    if streaming_message_id:
        if message.message_id == int(streaming_message_id):

            stream_dict = create_stream_dict(message)

            stream_count = len(stream_dict.keys())

            if stream_count > 3:
                stream_count = 3

            request_urls_list = assemble_requests(vmix_ip, stream_dict, stream_autorun, stream_count)

            print(request_urls_list)

            if not check_active_streaming(vmix_ip):

                if send_stream_requests(request_urls_list):

                    bot.send_message(message.chat.id, "Ссылка и ключ были внесены для "+str(stream_count) +
                                 " потоков на Vmix " + vmix_number)

                if check_active_streaming(vmix_ip):
                    bot.send_message(message.chat.id, "Потоки на Vmix"+vmix_number+" запущены")
                reset_global_values()

            """else:
                bot.send_message(message.chat.id, "Активен стрим на Vmix "+vmix_number +
                                 "!\n Параметры потоков не изменены.")"""
            start_message(message)


def get_vmix_ip(vmix_number):
    try:
        vmix_ip = vmix_ip_dict[int(vmix_number)]

        return vmix_ip
    except:

        print("Нет у нас такого vmix")


def create_stream_dict(message):
    stream_dict = {}
    for n in range(len(message.text.splitlines())):
        if "/" in message.text.splitlines()[n]:
            try:
                if len(message.text.splitlines()[n + 1]) > 5:
                    stream_dict[message.text.splitlines()[n]] = message.text.splitlines()[n + 1]
                else:
                    stream_dict[message.text.splitlines()[n]] = message.text.splitlines()[n + 2]
            except:
                print("Нет строки с ключом")
        elif "ют" in message.text.splitlines()[n].lower():
            if len(message.text.splitlines()[n + 1]) > 5:
                stream_dict["rtmp://a.rtmp.youtube.com/live2"] = message.text.splitlines()[n + 1]
            else:
                stream_dict["rtmp://a.rtmp.youtube.com/live2"] = message.text.splitlines()[n + 2]

    return stream_dict


def assemble_requests(vmix_ip, stream_dict, stream_autorun, stream_count):
    requests_list = []

    for stream in range(stream_count):        # Create requests for stream urls & keys
        request_set_url = "http://" + vmix_ip + ":8088/api/?Function=StreamingSetURL&Value=" + str(stream) + "," + \
                  list(stream_dict.keys())[stream]
        requests_list.append(request_set_url)
        request_set_stream_key = "http://" + vmix_ip + ":8088/api/?Function=StreamingSetKey&Value=" + str(stream) + \
                                 "," + stream_dict[list(stream_dict.keys())[stream]]
        requests_list.append(request_set_stream_key)

        if stream_autorun:

            request_start_stream = "http://" + vmix_ip + ":8088/api/?Function=StartStreaming&Value=" + str(stream)

            requests_list.append(request_start_stream)

    return requests_list


def send_stream_requests(request_urls_list):

    for request_url in request_urls_list:

        request = requests.get(request_url)

        if request.status_code == "500":
            print("500")
            return False

    return True


def check_active_streaming(vmix_ip):

    url = "http://"+vmix_ip+":8088/api/"
    request = requests.get(url)
    active_streaming = request.text.find("<streaming>True</streaming>").bit_length()
    if active_streaming == 11:
        return True
    else:
        return False


def stop_stream(vmix_ip):

    request_urls_list = ["http://" + vmix_ip + ":8088/api/?Function=StopStreaming"]

    send_stream_requests(request_urls_list)


def reset_global_values():
    global stream_autorun
    global streaming_message_id
    global vmix_number
    global vmix_ip

    stream_autorun = False
    streaming_message_id = ""
    vmix_number = ""
    vmix_ip = ""


def get_last_records(smena, records):
    for user_chat_id in smena:

        if user_chat_id:

            try:
                raw_response = requests.get(url=url, auth=(login, password), params={'days': records}, timeout=40)

                response_dict = json.loads(raw_response.text)

                last_records = format_last_records(response_dict)

                bot.send_message(user_chat_id, last_records)

            except:

                print("JSON load error")


def format_last_records(response_dict):
    last_records = ''

    for record in response_dict:
        if isinstance(record.get("text"), str) and len(response_dict) > 1 and isinstance(record.get('author_name'), str):
            date = record.get('report_date')
            last_records += str((datetime.strptime(date, "%Y-%m-%d")).strftime("%d.%m.%Y"))
            last_records += ' ' + record.get('author_name') + ': \n'
            last_records += record.get('text') + '\n\n'
        else:
            # print("Нет текста отчета: " + record.text + record.report_date)
            last_records = False
            break
    return last_records


@bot.message_handler(commands=['otpuska'])
def otpuska(chatid, messageid):
    vac = open('График отпусков 2020.ods', 'rb')
    keyboard = create_keyboard(chatid)
    bot.delete_message(chatid, messageid)
    bot.send_document(chatid, vac)
    bot.send_message(chatid, 'Выберите раздел: ', reply_markup=keyboard)


@bot.message_handler(commands=['ip'])
def ip_adr(chatid, messageid):
    ip = open('IP адреса.ods', 'rb')
    keyboard = create_keyboard(chatid)
    bot.delete_message(chatid, messageid)
    bot.send_document(chatid, ip)
    bot.send_message(chatid, 'Выберите раздел: ', reply_markup=keyboard)


@bot.message_handler(commands=['asb3bank'])
def asb3bank(chatid, messageid):
    a3b = open('ASB3Bank.odt', 'rb')
    keyboard = create_keyboard(chatid)
    bot.delete_message(chatid, messageid)
    bot.send_document(chatid, a3b)
    bot.send_message(chatid, 'Выберите раздел: ', reply_markup=keyboard)


@bot.message_handler(commands=['cameras'])
def cameras_list(chatid, messageid):
    keyboard = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton(text='Назад', callback_data='back')
    buttons = [types.InlineKeyboardButton(text=key, callback_data=key) for key in Files.keys()]
    keyboard.add(*buttons)
    if chatid == 147314671 or 1019904124:
        add_button = types.InlineKeyboardButton(text='Добавить', callback_data='add,cameras_list')
        delete_button = types.InlineKeyboardButton(text='Удалить', callback_data='delete,cameras_list')
        keyboard.add(add_button, delete_button)
    keyboard.add(back_button)
    bot.edit_message_text(text='Выберите программу:', chat_id=chatid, message_id=messageid, reply_markup=keyboard)


@bot.message_handler(commands=['schemes'])
def schemes_list(chatid, messageid):
    keyboard = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton(text='Назад', callback_data='back')
    buttons = [types.InlineKeyboardButton(text=key, callback_data=key) for key in Schemes.keys()]
    keyboard.add(*buttons)
    if chatid == 147314671 or 1019904124:
        add_button = types.InlineKeyboardButton(text='Добавить', callback_data='add,schemes_list')
        delete_button = types.InlineKeyboardButton(text='Удалить', callback_data='delete,schemes_list')
        keyboard.add(add_button, delete_button)
    keyboard.add(back_button)
    bot.edit_message_text(text='Выберите схему:', chat_id=chatid, message_id=messageid, reply_markup=keyboard)


@bot.message_handler(commands=['zoom'])
def zoom_list(chatid, messageid):
    keyboard = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton(text='Назад', callback_data='back')
    buttons = [types.InlineKeyboardButton(text=key, callback_data=key) for key in ZOOM.keys()]
    keyboard.add(*buttons)
    if chatid == 147314671 or 1019904124:
        add_button = types.InlineKeyboardButton(text='Добавить', callback_data='add,zoom_list')
        delete_button = types.InlineKeyboardButton(text='Удалить', callback_data='delete,zoom_list')
        keyboard.add(add_button, delete_button)
    keyboard.add(back_button)
    bot.edit_message_text(text='Выберите конфигурацию:', chat_id=chatid, message_id=messageid, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in commands_string)
def callback_clearfunc(callback_query):
    chatid = callback_query.message.chat.id
    messageid = callback_query.message.message_id
    text = callback_query.data
    func_name = text + '(' + str(chatid) + ',' + str(messageid) + ')'
    eval(func_name)


@bot.callback_query_handler(func=lambda call: call.data in Files)
def callback_cameras(callback_query):
    chatid = callback_query.message.chat.id
    messageid = callback_query.message.message_id
    text = str(callback_query.data)
    cameras_send(str(text), chatid, messageid)


@bot.callback_query_handler(func=lambda call: call.data in Schemes)
def callback_schemes(callback_query):
    chatid = callback_query.message.chat.id
    messageid = callback_query.message.message_id
    text = str(callback_query.data)
    schemes_send(str(text), chatid, messageid)


@bot.callback_query_handler(func=lambda call: call.data in ZOOM)
def callback_zoom(callback_query):
    chatid = callback_query.message.chat.id
    messageid = callback_query.message.message_id
    text = str(callback_query.data)
    zoom_send(str(text), chatid, messageid)


@bot.callback_query_handler(func=lambda call: 'delete' in call.data)
def delete_mode(callback_query):

    chatid = callback_query.message.chat.id
    messageid = callback_query.message.message_id


    text = str(callback_query.data)

    calldata_list = text.split(',', 1)


    argument = calldata_list[1]


    if argument == 'cameras_list':

        keyboard = types.InlineKeyboardMarkup()
        buttons = [types.InlineKeyboardButton(text=key, callback_data='remove,'+key) for key in Files.keys()]
        ready_button = types.InlineKeyboardButton(text='Готово', callback_data='ready,'+argument)

        keyboard.add(*buttons)
        keyboard.add(ready_button)
        bot.edit_message_text(text='Удаление расстановки камер (по нажатию "Готово"):', chat_id=chatid, message_id=messageid, reply_markup=keyboard)

    if argument == 'schemes_list':

        keyboard = types.InlineKeyboardMarkup()
        buttons = [types.InlineKeyboardButton(text=key, callback_data='remove,'+key) for key in Schemes.keys()]
        ready_button = types.InlineKeyboardButton(text='Готово', callback_data='ready,'+argument)

        keyboard.add(*buttons)
        keyboard.add(ready_button)
        bot.edit_message_text(text='Удаление схем (по нажатию "Готово"):', chat_id=chatid, message_id=messageid, reply_markup=keyboard)

    if argument == 'zoom_list':

        keyboard = types.InlineKeyboardMarkup()
        buttons = [types.InlineKeyboardButton(text=key, callback_data='remove,'+key) for key in ZOOM.keys()]
        ready_button = types.InlineKeyboardButton(text='Готово', callback_data='ready,' + argument)

        keyboard.add(*buttons)
        keyboard.add(ready_button)
        bot.edit_message_text(text='Удаление zoom (по нажатию "Готово"):', chat_id=chatid, message_id=messageid, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: 'add' in call.data)
def add_mode(callback_query):

    chatid = callback_query.message.chat.id
    messageid = callback_query.message.message_id


    text = str(callback_query.data)

    calldata_list = text.split(',', 1)

    global argument

    argument = calldata_list[1]


    if argument == 'cameras_list':

        keyboard = types.InlineKeyboardMarkup()
        buttons = [types.InlineKeyboardButton(text=key, callback_data=key) for key in Files.keys()]
        back_button = types.InlineKeyboardButton(text='Назад', callback_data='back')
        keyboard.add(*buttons)
        keyboard.add(back_button)

        bot.edit_message_text(text='Добавить расстановку камер - отправить фото, название из подписи фото',
                              chat_id=chatid, message_id=messageid, reply_markup=keyboard)

    if argument == 'schemes_list':

        keyboard = types.InlineKeyboardMarkup()
        buttons = [types.InlineKeyboardButton(text=key, callback_data=key) for key in Schemes.keys()]
        back_button = types.InlineKeyboardButton(text='Назад', callback_data='back')
        keyboard.add(*buttons)
        keyboard.add(back_button)
        bot.edit_message_text(text='Добавить схему - отправить документ(pdf), название из подписи документа',
                              chat_id=chatid, message_id=messageid, reply_markup=keyboard)

    if argument == 'zoom_list':

        keyboard = types.InlineKeyboardMarkup()
        buttons = [types.InlineKeyboardButton(text=key, callback_data=key) for key in ZOOM.keys()]
        back_button = types.InlineKeyboardButton(text='Назад', callback_data='back')
        keyboard.add(*buttons)
        keyboard.add(back_button)
        bot.edit_message_text(text='Добавить конфигурацию Zoom - отправить фото, название из подписи фото',
                              chat_id=chatid, message_id=messageid, reply_markup=keyboard)

    return argument



@bot.callback_query_handler(func=lambda call: 'ready' in call.data)
def ready_mode(callback_query):

    chatid = callback_query.message.chat.id
    messageid = callback_query.message.message_id

    text = str(callback_query.data)
    calldata_list = text.split(',', 1)

    argument = calldata_list[1]

    if argument == 'cameras_list':

        cameras_list(chatid, messageid)

    if argument == 'schemes_list':

        schemes_list(chatid, messageid)

    if argument == 'zoom_list':

        zoom_list(chatid, messageid)


@bot.callback_query_handler(func=lambda call: 'remove' in call.data)
def remove_cell(callback_query):

    chatid = callback_query.message.chat.id
    messageid = callback_query.message.message_id

    text = str(callback_query.data)
    calldata_list = text.split(',', 1)

    argument = calldata_list[1]

    global SchemesV
    global FilesV
    global ZOOMV

    if argument in SchemesV:

        Schemes.pop(argument)

        save_values()

    if argument in FilesV:

        Files.pop(argument)

        save_values()

    if argument in ZOOMV:

        ZOOM.pop(argument)

        save_values()


@bot.message_handler(content_types=['photo'])
def add_image(message):

        global SchemesV
        global FilesV
        global ZOOMV

        global argument

        chatid = message.chat.id

        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        if argument == 'main':
            src = os.getcwd()

        if argument == 'cameras_list':
            src = dest_cameras

            FilesV[message.caption] = message.caption+'.jpg'

            save_values()

        if argument == 'zoom_list':
            src = dest_ZOOM

            ZOOMV[message.caption] = message.caption + '.jpg'
            save_values()

        script_dest = os.getcwd()

        os.chdir(src)

        with open(message.caption + '.jpg', 'wb+') as new_file:
            new_file.write(downloaded_file)

        keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton(text='Назад', callback_data='back')
        keyboard.add(back_button)

        bot.send_message(text=message.caption + ' добавлено', chat_id=chatid, reply_markup=keyboard)

        os.chdir(script_dest)


@bot.message_handler(content_types=['document'])
def add_doc(message):

        global SchemesV
        global FilesV
        global ZOOMV

        global argument

        chatid = message.chat.id
        file_id_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_id_info.file_path)

        if argument == 'schemes_list':
            src = dest_schemes

            SchemesV[message.caption] = message.caption + '.pdf'
            save_values()

            script_dest = os.getcwd()

            os.chdir(src)

            with open(message.caption + '.pdf', 'wb+') as new_file:
                new_file.write(downloaded_file)

            keyboard = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton(text='Назад', callback_data='back')
            keyboard.add(back_button)

            bot.send_message(text=message.caption+' добавлено', chat_id=chatid, reply_markup=keyboard)

            os.chdir(script_dest)


@bot.callback_query_handler(func=lambda call: 'back' in call.data)
def go_to_main(callback_query):

    chatid = callback_query.message.chat.id

    keyboard = create_keyboard(chatid)
    chatid = callback_query.message.chat.id
    messageid = callback_query.message.message_id
    bot.edit_message_text('Выберите раздел:', chatid, messageid, reply_markup=keyboard)


def save_values():
    f = open('DB.py', 'w')
    f.write(
        str('Files = ' + str(FilesV)) + '\n' + str('Schemes = ' + str(SchemesV) + '\n' + str('ZOOM = ' + str(ZOOMV)) +
                                                   '\n' + str(smena_1) + '\n' + str(smena_2) + '\n' +
                                                   str(smena_3) + '\n' + str(smena_4) + '\n' +
                                                   str(every_day)))
    f.close()


if __name__ == '__main__':

    scheduler = BackgroundScheduler(timezone='Europe/Moscow')

    scheduler.add_job(lambda: get_last_records(smena=every_day, records=1), trigger='interval', days=1, start_date=start_date_every_day, name="last_records_for_every_day", id='last_records_for_every_day')

    scheduler.add_job(lambda: get_last_records(smena=smena_1, records=3), trigger='interval', days=4,
                      start_date=start_date_smena_1, name="last_records_for_smena_1", id='last_records_for_smena_1')

    scheduler.add_job(lambda: get_last_records(smena=smena_2, records=3), trigger='interval', days=4,
                      start_date=start_date_smena_2, name="last_records_for_smena_2", id='last_records_for_smena_2')

    scheduler.add_job(lambda: get_last_records(smena=smena_3, records=3), trigger='interval', days=4,
                      start_date=start_date_smena_3, name="last_records_for_smena_3", id='last_records_for_smena_3')

    scheduler.add_job(lambda: get_last_records(smena=smena_4, records=3), trigger='interval', days=4,
                      start_date=start_date_smena_4, name="last_records_for_smena_4", id='last_records_for_smena_4')

    scheduler.print_jobs()

    scheduler.start()

    try:
        bot.infinity_polling(True)
    except:
        time.sleep(5)
        os.system('python 360_eng_assist.py &')
