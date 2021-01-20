import telebot
import os
import time
from token import TOKEN
from config import dest_cameras, dest_schemes, dest_ZOOM, dest_script
from DB import Files, Schemes, ZOOM

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет! Выбери нужный раздел: /cameras /schemes /ZOOM /otpuska /ip /asb3bank')

@bot.message_handler(commands=['otpuska'])
def vacs (message):
    vac = open('/root/Telegram/360_eng_assist/График отпусков 2020.ods', 'rb')
    bot.send_document(message.chat.id, vac)

@bot.message_handler(commands=['ip'])
def ip_adr (message):
    ip_adr = open('/root/Telegram/360_eng_assist/IP адреса.ods', 'rb')
    bot.send_document(message.chat.id, ip_adr)

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
def asb3bank (message):
    asb3bank = open('/root/Telegram/360_eng_assist/asb3bank.png', 'rb')
    bot.send_document(message.chat.id, asb3bank)

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
        time.sleep(40)
        os.command(dest_script)
