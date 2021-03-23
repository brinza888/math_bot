# -*- coding: utf-8 -*-
import telebot
from telebot import types
import urllib
from io import BytesIO
from PIL import Image
from collections import deque

with open("token.txt") as tk:
    bot = telebot.TeleBot(tk.read())


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(types.KeyboardButton('Помощь'))
    send_mess = f"<b>Привет {message.from_user.first_name} {message.from_user.last_name}!</b>\nНажми на кнопку, чтобы узнать, что я умею"
    bot.send_message(message.chat.id, send_mess, parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    get_message_bot = message.text.strip().lower()

    if get_message_bot == 'помощь':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(types.KeyboardButton('Список операторов'))
        final_message = 'Я бот, который умеет строить таблицы истинности'
        bot.send_message(message.chat.id, final_message, parse_mode='html', reply_markup=markup)
    elif get_message_bot == 'список операторов':
        final_message = '<b>Выберите команду:</b> \n <b>~</b> : Логическое отрицание \n <b>&</b> : Конъюнкция \n <b>|</b> : Дизъюнкция \n <b>></b> Импликация \n <b>^</b> : Исключающее или \n <b>=</b> : Эквиваленция'
        bot.send_message(message.chat.id, final_message, parse_mode='html' )
    elif 'гей' in get_message_bot:
        final_message = f"{message.from_user.first_name}, сам гей"
        bot.send_message(message.chat.id, final_message, parse_mode='html')
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(types.KeyboardButton('Помощь'))
        final_message = BytesIO(urllib.request.urlopen('https://www.meme-arsenal.com/memes/ddcf6ef709b8db99da11efd281abd990.jpg').read())
        bot.send_photo(message.chat.id, final_message)


bot.polling(none_stop=True)
