import telebot
import os
import time
from ntoken import TOKEN
from config import dest_cameras, dest_schemes, dest_ZOOM, dest_script
from DB import Files, Schemes, ZOOM
from telebot import types

bot = telebot.TeleBot(TOKEN)

commands_for_buttons = ['otpuska', 'ip_adr', 'asb3bank']


def create_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=c, callback_data=c) for c in commands_for_buttons]
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
def list(message):
    for key in Files:
        bot.send_message(message.chat.id, key)


@bot.message_handler(commands=['schemes'])
def list(message):
    for key in Schemes:
        bot.send_message(message.chat.id, key)


@bot.message_handler(commands=['ZOOM'])
def list(message):
    for key in ZOOM:
        bot.send_message(message.chat.id, key)

@bot.message_handler(commands=['asb3bank'])
def asb3bank(messageid):
    asb3bank = open('asb3bank.png', 'rb')
    keyboard = create_keyboard()
    bot.send_document(messageid, asb3bank, reply_markup=keyboard)

def testfunc(messageid):
    bot.send_message(messageid, 'testfuncworks')


@bot.callback_query_handler(func=lambda x: True)
def callback_handler(callback_query):
    messageid = callback_query.message.chat.id
    text = callback_query.data
    func_name = text+'('+str(messageid)+')'
    eval(func_name)


@bot.message_handler(content_types=["text"])
def arrangement(message):
    coin_num = 0
    for key in Files:
        if message.text.lower() == key:
            coin_num = 1
            img = open(dest_cameras + Files.get(key), 'rb')
            bot.send_photo(message.chat.id, img)
            break
    for key in Schemes:
        if message.text.lower() == key:
            coin_num = 2
            doc = open(dest_schemes + Schemes.get(key), 'rb')
            bot.send_document(message.chat.id, doc)
            break
    for key in ZOOM:
        if message.text.lower() == key:
            coin_num = 3
            img = open(dest_ZOOM + ZOOM.get(key), 'rb')
            bot.send_photo(message.chat.id, img)
            break
    if coin_num == 0:
        bot.send_message(message.chat.id, 'нет такой команды')


if __name__ == '__main__':
    try:
        bot.infinity_polling()
    except:
        time.sleep(10)
        os.system('python 360_eng_assist.py &')
