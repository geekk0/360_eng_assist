import telebot
import os
import time
from ntoken import TOKEN
from config import dest_cameras, dest_schemes, dest_ZOOM
from DB import Files, Schemes, ZOOM
from telebot import types

bot = telebot.TeleBot(TOKEN)

commands_for_buttons = {'otpuska': 'Отпуска', 'ip_adr': 'ip', 'asb3bank': 'asb3bank', 'schemes_list': 'Схемы', 'cameras_list': 'Камеры', 'zoom_list': 'Zoom'}


def create_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    buttons = [types.InlineKeyboardButton(text=commands_for_buttons[key], callback_data=key)
    for key in commands_for_buttons.keys()]
    keyboard.add(*buttons)
    return keyboard


@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = create_keyboard()
    bot.send_message(message.chat.id, 'Привет! Выбери нужный раздел: /cameras /schemes /ZOOM /otpuska /ip /asb3bank', reply_markup=keyboard)


@bot.message_handler(commands=['otpuska'])
def otpuska(messageid):
    vac = open('График отпусков 2020.ods', 'rb')
    keyboard = create_keyboard()
    bot.send_document(messageid, vac, reply_markup=keyboard)


@bot.message_handler(commands=['ip'])
def ip_adr(messageid):
    ip_adr = open('IP адреса.ods', 'rb')
    keyboard = create_keyboard()
    bot.send_document(messageid, ip_adr, reply_markup=keyboard)


@bot.message_handler(commands=['cameras'])
def cameras_list(messageid):
    for key in Files:
        bot.send_message(messageid, key)


@bot.message_handler(commands=['schemes'])
def schemes_list(messageid):
    for key in Schemes:
        bot.send_message(messageid, key)


@bot.message_handler(commands=['ZOOM'])
def zoom_list(messageid):
    for key in ZOOM:
        bot.send_message(messageid, key)


@bot.message_handler(commands=['asb3bank'])
def asb3bank(messageid):
    asb3bank = open('asb3bank.png', 'rb')
    keyboard = create_keyboard()
    bot.send_document(messageid, asb3bank, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda x: True)
def callback_handler(callback_query):
    messageid = callback_query.message.chat.id
    text = callback_query.data
    func_name = text+'('+str(messageid)+')'
    eval(func_name)


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
        time.sleep(10)
        os.system('python 360_eng_assist.py &')
