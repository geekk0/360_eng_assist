import requests
import telebot
import os
import time
import json
from ntoken import TOKEN
from config import dest_cameras, dest_schemes, dest_ZOOM
from DB import Files, Schemes, ZOOM
from telebot import types

bot = telebot.TeleBot(TOKEN)

argument = 'main'

SchemesV = Schemes
FilesV = Files
ZOOMV = ZOOM

commands_for_buttons = {'otpuska': 'Отпуска', 'ip_adr': 'ip', 'asb3bank': 'asb3bank', 'schemes_list': 'Схемы',
                        'cameras_list': 'Камеры', 'zoom_list': 'Zoom'}
commands_string = ''.join('{}{}'.format(key, val) for key, val in commands_for_buttons.items())


def create_keyboard(chatid):
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    buttons = [types.InlineKeyboardButton(text=commands_for_buttons[key], callback_data=key)
               for key in commands_for_buttons.keys()]

    keyboard.add(*buttons)

    add_button = types.InlineKeyboardButton(text='Добавить', callback_data='add, main')
    delete_button = types.InlineKeyboardButton(text='Удалить', callback_data='delete, main')
    if chatid == 147314671:

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
    if chatid == 147314671:
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
    if chatid == 147314671:
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
    if chatid == 147314671:
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



@bot.message_handler(commands=['poslednie_otcheti'])
def poslednie_otcheti(message):
    raw_response = requests.get(url='http://188.225.38.178:8888/api/last_records/', auth=('360_admin', 'X5mYdBZ984aqFHoN'),
                                params={'days': '1'})
    print(raw_response.url)
    response_dict = json.loads(raw_response.text)

    last_records = get_last_records(response_dict)

    if last_records:
        bot.send_message(message.chat.id, last_records)
    else:
        bot.send_message(message.chat.id, 'no response')


def get_last_records(response_dict):
    last_records = ''

    for record in response_dict:
        last_records += record.get('report_date')
        last_records += ' ' + record.get('author_name') + ': \n'
        last_records += record.get('text') + '\n\n'

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
    if chatid == 147314671:
        add_button = types.InlineKeyboardButton(text='Добавить', callback_data='add,schemes_list')
        delete_button = types.InlineKeyboardButton(text='Удалить', callback_data='delete,schemes_list')
        keyboard.add(add_button, delete_button)
    keyboard.add(back_button)
    bot.edit_message_text(text='Выберите программу:', chat_id=chatid, message_id=messageid, reply_markup=keyboard)


@bot.message_handler(commands=['schemes'])
def schemes_list(chatid, messageid):
    keyboard = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton(text='Назад', callback_data='back')
    buttons = [types.InlineKeyboardButton(text=key, callback_data=key) for key in Schemes.keys()]
    keyboard.add(*buttons)
    if chatid == 147314671:
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
    if chatid == 147314671:
        add_button = types.InlineKeyboardButton(text='Добавить', callback_data='add,schemes_list')
        delete_button = types.InlineKeyboardButton(text='Удалить', callback_data='delete,schemes_list')
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
        bot.edit_message_text(text='Удаление схем (по нажатию "Готово"):', chat_id=chatid, message_id=messageid, reply_markup=keyboard)


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

        f = open('DB.py', 'w')
        f.write(str('Files = ' + str(FilesV))+'\n'+str('Schemes = ' + str(SchemesV)+'\n'+str('ZOOM = ' + str(ZOOMV))))
        f.close()

    if argument in FilesV:

        Files.pop(argument)

        f = open('DB.py', 'w')
        f.write(str('Files = ' + str(FilesV))+'\n'+str('Schemes = ' + str(SchemesV)+'\n'+str('ZOOM = ' + str(ZOOMV))))
        f.close()

    if argument in ZOOMV:

        ZOOM.pop(argument)

        f = open('DB.py', 'w')
        f.write(str('Files = ' + str(FilesV))+'\n'+str('Schemes = ' + str(SchemesV)+'\n'+str('ZOOM = ' + str(ZOOMV))))
        f.close()


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
            f = open('DB.py', 'w')
            f.write(str('Files = ' + str(FilesV)) + '\n' + str(
                'Schemes = ' + str(SchemesV) + '\n' + str('ZOOM = ' + str(ZOOMV))))
            f.close()

        if argument == 'zoom_list':
            src = dest_ZOOM

            ZOOMV[message.caption] = message.caption + '.jpg'
            f = open('DB.py', 'w')
            f.write(str('Files = ' + str(FilesV)) + '\n' + str(
                'Schemes = ' + str(SchemesV) + '\n' + str('ZOOM = ' + str(ZOOMV))))
            f.close()

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
            f = open('DB.py', 'w')
            f.write(str('Files = ' + str(FilesV)) + '\n' + str(
                'Schemes = ' + str(SchemesV) + '\n' + str('ZOOM = ' + str(ZOOMV))))
            f.close()

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


if __name__ == '__main__':
    try:
        bot.infinity_polling(True)
    except:
        time.sleep(5)
        os.system('python 360_eng_assist.py &')
