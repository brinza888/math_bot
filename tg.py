# -*- coding: utf-8 -*-

import os
import sys
from io import StringIO

import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from logic import build_table, OPS
from matrix import Matrix, SizesMatchError, SquareMatrixRequired


# max size available for matrix is
MAX_MATRIX = 8

# generate supported operators description
ops_description = '\n'.join([f'<b>{op}</b> {op_data[3]}' for op, op_data in OPS.items()])

if not os.path.isfile('token.txt'):  # check if token.txt exists
    print('Bot API token should be passed in token.txt file', file=sys.stderr)
    exit(1)

with open('token.txt') as tk:  # attempt to read api token
    bot = telebot.TeleBot(tk.read().strip())


menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)  # this markup is bot menu
menu.add(KeyboardButton('/logic'))
menu.add(KeyboardButton('/matrix'))
menu.add(KeyboardButton('/help'))


hide_menu = ReplyKeyboardRemove()  # sending this as reply_markup will close menu


@bot.message_handler(commands=['start'])
def start_message(message):
    send_mess = (f'<b>Привет, {message.from_user.first_name} {message.from_user.last_name}!</b>\n'
                 f'Используй клавиатуру или команды для вызова нужной фишки\n'
                 f'/help - вызов помощи')
    bot.send_message(message.chat.id, send_mess, parse_mode='html', reply_markup=menu)


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id,
                     ('/matrix для нахождения определителя матрицы (не более чем 8x8).\n'
                      '/logic для построения таблицы истинности логического выражения.\n'
                      'Описание допустимых логических операторов:\n'
                      f'{ops_description}'),
                     parse_mode='html')


@bot.message_handler(commands=['matrix', 'det'])
def matrix_input(message):
    send_matrix = bot.send_message(message.chat.id, 'Введите матрицу: (одним сообщением)', reply_markup=hide_menu)
    bot.register_next_step_handler(send_matrix, matrix_output)


def matrix_output(message):
    try:
        lst = [[float(x) for x in row.split()] for row in message.text.split('\n')]
        n = len(lst)
        matrix = Matrix(n, n, 0)
        matrix.fill(lst)
        if matrix.n > MAX_MATRIX or matrix.m > MAX_MATRIX:
            bot.send_message(message.chat.id,
                             f'Размер матрицы не должен превышать {MAX_MATRIX}x{MAX_MATRIX} =(',
                             reply_markup=menu)
            return
        answer = matrix.det()
    except SizesMatchError:
        bot.send_message(message.chat.id,
                         'Расхождение размеров строк и столбцов. Ожидилась <b>квадратная</b> матрица!',
                         parse_mode='html',
                         reply_markup=menu)
    except (SquareMatrixRequired, ValueError):
        bot.send_message(message.chat.id,
                         'Необходимо вводить <b>числовую</b> квадратную матрицу',
                         reply_markup=menu,
                         parse_mode='html')
    else:
        bot.send_message(message.chat.id, str(answer), reply_markup=menu)


@bot.message_handler(commands=['logic', 'exp'])
def logic_input(message):
    send_logic = bot.send_message(message.chat.id, 'Введите логическое выражение:', reply_markup=hide_menu)
    bot.register_next_step_handler(send_logic, logic_output)


def logic_output(message):
    try:
        table, variables = build_table(message.text)
        out = StringIO()  # abstract file (file-object)
        print(*variables, 'F', file=out, sep=' '*2)
        for row in table:
            print(*row, file=out, sep=' '*2)
        bot.send_message(message.chat.id, f'<code>{out.getvalue()}</code>', parse_mode='html', reply_markup=menu)
    except (AttributeError, SyntaxError):
        bot.send_message(message.chat.id, "Ошибка ввода данных", reply_markup=menu)


if __name__ == '__main__':
    bot.polling(none_stop=True)
