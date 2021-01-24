import telebot
import os
import time
from ntoken import TOKEN
from config import dest_cameras, dest_schemes, dest_ZOOM
from DB import Files, Schemes, ZOOM
from telebot import types

bot = telebot.TeleBot(TOKEN)

commands_for_buttons = {'otpuska': 'Отпуска', 'ip_adr': 'ip', 'asb3bank': 'asb3bank', 'schemes_list': 'Схемы', 'cameras_list': 'Камеры', 'zoom_list': 'Zoom'}
commands_string = ''.join('{}{}'.format(key, val) for key, val in commands_for_buttons.items())


def create_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    buttons = [types.InlineKeyboardButton(text=commands_for_buttons[key], callback_data=key)
    for key in commands_for_buttons.keys()]
    keyboard.add(*buttons)
    return keyboard


def cameras_send(cam_file, chatid, messageid):
    img = open(dest_cameras + Files.get(cam_file), 'rb')
    bot.send_photo(chatid, img)
    keyboard = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton(text='Назад', callback_data='back')
    buttons = [types.InlineKeyboardButton(text=key, callback_data=key)
    for key in Files.keys()]
    keyboard.add(*buttons)
    keyboard.add(back_button)
    bot.delete_message(chatid, messageid)
    bot.send_message(chatid, text='Выберите программу:', reply_markup=keyboard)


def schemes_send(scheme_file, chatid, messageid):
    doc = open(dest_schemes + Schemes.get(scheme_file), 'rb')
    bot.send_document(chatid, doc)
    keyboard = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton(text='Назад', callback_data='back')
    buttons = [types.InlineKeyboardButton(text=key, callback_data=key)
               for key in Schemes.keys()]
    keyboard.add(*buttons)
    keyboard.add(back_button)
    bot.delete_message(chatid, messageid)
    bot.send_message(chatid, text='Выбери схему:', reply_markup=keyboard)


def zoom_send(zoom_file, chatid, messageid):
    img = open(dest_ZOOM + ZOOM.get(zoom_file), 'rb')
    bot.send_photo(chatid, img)
    keyboard = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton(text='Назад', callback_data='back')
    buttons = [types.InlineKeyboardButton(text=key, callback_data=key)
               for key in ZOOM.keys()]
    keyboard.add(*buttons)
    keyboard.add(back_button)
    bot.delete_message(chatid, messageid)
    bot.send_message(chatid, text='Выбери тип трансляции:', reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = create_keyboard()
    bot.send_message(message.chat.id, 'Привет! Жмякай нужный пункт меню', reply_markup=keyboard)


@bot.message_handler(commands=['otpuska'])
def otpuska(chatid, messageid):
    vac = open('График отпусков 2020.ods', 'rb')
    keyboard = create_keyboard()
    bot.send_document(chatid, vac, reply_markup=keyboard)
    bot.delete_message(chatid, messageid)



@bot.message_handler(commands=['ip'])
def ip_adr(chatid, messageid):
    ip = open('IP адреса.ods', 'rb')
    keyboard = create_keyboard()
    bot.send_document(chatid, ip, reply_markup=keyboard)
    bot.delete_message(chatid, messageid)


@bot.message_handler(commands=['asb3bank'])
def asb3bank(chatid, messageid):
    a3b = open('ASB3Bank.odt', 'rb')
    keyboard = create_keyboard()
    bot.send_document(chatid, a3b, reply_markup=keyboard)
    bot.delete_message(chatid, messageid)


@bot.message_handler(commands=['cameras'])
def cameras_list(chatid, messageid):
    keyboard = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton(text='Назад', callback_data='back')
    buttons = [types.InlineKeyboardButton(text=key, callback_data=key) for key in Files.keys()]
    keyboard.add(*buttons)
    keyboard.add(back_button)
    bot.edit_message_reply_markup(chatid, messageid, reply_markup=keyboard)


@bot.message_handler(commands=['schemes'])
def schemes_list(chatid, messageid):
    keyboard = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton(text='Назад', callback_data='back')
    buttons = [types.InlineKeyboardButton(text=key, callback_data=key) for key in Schemes.keys()]
    keyboard.add(*buttons)
    keyboard.add(back_button)
    bot.edit_message_reply_markup(chatid, messageid, reply_markup=keyboard)


@bot.message_handler(commands=['schemes'])
def zoom_list(chatid, messageid):
    keyboard = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton(text='Назад', callback_data='back')
    buttons = [types.InlineKeyboardButton(text=key, callback_data=key) for key in ZOOM.keys()]
    keyboard.add(*buttons)
    keyboard.add(back_button)
    bot.edit_message_reply_markup(chatid, messageid, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in commands_string)
def callback_clearfunc(callback_query):
    chatid = callback_query.message.chat.id
    messageid = callback_query.message.message_id
    text = callback_query.data
    func_name = text+'('+str(chatid)+','+str(messageid)+')'
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


@bot.callback_query_handler(func=lambda call: 'back')
def go_to_main(callback_query):
    keyboard = create_keyboard()
    chatid = callback_query.message.chat.id
    messageid = callback_query.message.message_id
    bot.edit_message_reply_markup(chatid, messageid, reply_markup=keyboard)


@bot.message_handler(content_types=["text"])
def arrangement(message):

    for key in Files:
        if message.text.lower() == key:
            img = open(dest_cameras + Files.get(key), 'rb')
            bot.send_photo(message.chat.id, img)
            break
    for key in Schemes:
        if message.text.lower() == key:
            doc = open(dest_schemes + Schemes.get(key), 'rb')
            bot.send_document(message.chat.id, doc)
            break
    for key in ZOOM:
        if message.text.lower() == key:
            img = open(dest_ZOOM + ZOOM.get(key), 'rb')
            bot.send_photo(message.chat.id, img)
            break


if __name__ == '__main__':
    try:
        bot.infinity_polling()
    except:
        time.sleep(5)
        os.system('python 360_eng_assist.py &')
