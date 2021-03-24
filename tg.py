# -*- coding: utf-8 -*-
import telebot
from telebot import types
import requests
from io import BytesIO

from logic import shunting_yard, calculate


r = requests.get('https://www.meme-arsenal.com/memes/ddcf6ef709b8db99da11efd281abd990.jpg')
MEM_IMAGE = BytesIO(r.content)  # BytesIO creates file-object from bytes string

operators = {
    "~": ("Логическое отрицание",),
    "&": ("Конъюнкция",),
    "|": ("Дизъюнкция",),
    ">": ("Импликация",),
    "^": ("Исключающее или",),
    "=": ("Эквиваленция",),
}

HELP_STR = "\n".join([f"<b>{op}</b> {op_info[0]}" for op, op_info in operators.items()])


with open("token.txt") as tk:
    bot = telebot.TeleBot(tk.read())


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(types.KeyboardButton('Помощь'))
    send_mess = f"<b>Привет {message.from_user.first_name} {message.from_user.last_name}!</b>\nНажми на кнопку, чтобы узнать, что я умею"
    bot.send_message(message.chat.id, send_mess, parse_mode='html', reply_markup=markup)


@bot.message_handler(regexp="help|ops|помощь")
def send_help(message):
    bot.send_message(message.chat.id, HELP_STR, parse_mode='html')


@bot.message_handler(regexp="&|\||>|~|\^|=")
def handle_ops(message):
    out, variables = shunting_yard(message.text)
    n = len(variables)
    var_pr=""

    for v in variables:
        var_pr+=str(v) + "    "
    var_pr+="F"+"\n"

    for i in range(2 ** n):
        values = [int(x) for x in bin(i)[2:].rjust(n, "0")]
        d = {variables[k]: values[k] for k in range(n)}

        for v in values:
            var_pr+=str(v) + "    "
        var_pr+=str(int(calculate(out, d))) + "\n"
    bot.send_message(message.chat.id, var_pr)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    get_message_bot = message.text.strip().lower()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)

    if get_message_bot == 'помощь':
        markup.add(types.KeyboardButton('Список операторов'))
        final_message = 'Я бот, который умеет строить таблицы истинности'
    elif get_message_bot == 'список операторов':
        final_message = HELP_STR
    elif 'гей' in get_message_bot:
        final_message = f"{message.from_user.first_name}, сам гей!"
    elif get_message_bot == 'ахуеть':
        final_message=MEM_IMAGE
    else:
        markup.add(types.KeyboardButton('Помощь'))


    if isinstance(final_message, BytesIO):
        bot.send_photo(message.chat.id, final_message, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, final_message, parse_mode='html', reply_markup=markup)


bot.polling(none_stop=True)
