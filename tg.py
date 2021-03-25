# -*- coding: utf-8 -*-
from io import BytesIO, StringIO  # from base-library

import requests  # from site-package
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from logic import build_table  # from your modules
from matrix import det


r = requests.get('https://www.meme-arsenal.com/memes/ddcf6ef709b8db99da11efd281abd990.jpg')
MEM_IMAGE = BytesIO(r.content)  # BytesIO creates file-object from bytes string

operators = {
    '~': ('Логическое отрицание',),
    '&': ('Конъюнкция',),
    '|': ('Дизъюнкция',),
    '>': ('Импликация',),
    '^': ('Исключающее или',),
    '=': ('Эквиваленция',),
}

HELP_STR = '\n'.join([f'<b>{op}</b> {op_info[0]}' for op, op_info in operators.items()])

with open('token.txt') as tk:
    bot = telebot.TeleBot(tk.read())


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(KeyboardButton('Помощь'))
    markup.add(KeyboardButton('Что ты умеешь?'))
    markup.add(KeyboardButton('Список операторов'))
    send_mess = (f'<b>Привет {message.from_user.first_name} {message.from_user.last_name}!</b>\n'
                 f'Нажми на кнопку, чтобы узнать, что я умею')
    bot.send_message(message.chat.id, send_mess, parse_mode='html', reply_markup=markup)


@bot.message_handler(regexp='список операторов')
def send_ops(message):
    bot.send_message(message.chat.id, HELP_STR, parse_mode='html')


@bot.message_handler(regexp='помощь')
def send_ops(message):
    bot.send_message(message.chat.id,
                     ('/matrix для нахождения определителя матрицы.\n'
                      '/logic для построения таблицы истинности логического выражения.'),
                     parse_mode='html')


@bot.message_handler(regexp='Что ты умеешь?')
def send_help(message):
    bot.send_message(message.chat.id,
                     'Я бот, который умеет строить таблицы истинности и считать определители матриц.',
                     parse_mode='html')


@bot.message_handler(commands=['matrix', 'det'])
def matrix_input(message):
    send_matrix = bot.send_message(message.chat.id, 'Введите матрицу:')
    bot.register_next_step_handler(send_matrix, matrix_output)


def matrix_output(message):
    try:
        matrix = [[float(x) for x in row.split()] for row in message.text.split('\n')]
        answer = det(matrix)
    except ValueError:
        bot.send_message(message.chat.id, 'Необходимо вводить числовую квадратную матрицу')
    except IndexError:
        bot.send_message(message.chat.id, 'Невозможно посчитать определитель матрицы')
    else:
        bot.send_message(message.chat.id, str(answer))


@bot.message_handler(commands=['logic', 'table'])
def logic_input(message):
    send_logic = bot.send_message(message.chat.id, 'Введите логическое выражение:')
    bot.register_next_step_handler(send_logic, logic_output)


def logic_output(message):
    table, variables = build_table(message.text)
    out = StringIO()  # abstract file (file-object)
    print(*variables, 'F', file=out, sep=' '*5)
    for row in table:
        print(*row, file=out, sep=' '*5)
    bot.send_message(message.chat.id, out.getvalue())


@bot.message_handler(regexp='ахуеть')  # отдельный хендлер картинки
def get_text_messages(message):
    bot.send_photo(message.chat.id, MEM_IMAGE)


bot.polling(none_stop=True)
