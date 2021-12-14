# -*- coding: utf-8 -*-

# Copyright (C) 2021 Ilya Bezrukov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import sys
from io import StringIO

import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from logic import build_table, OPS
from matrix import Matrix, SizesMatchError, SquareMatrixRequired
from rings import *


# max size available for matrix is
MAX_MATRIX = 8

# max rings modulo
MAX_MODULO = 10**15

# generate supported operators description
ops_description = '\n'.join([f'<b>{op}</b> {op_data[3]}' for op, op_data in OPS.items()])

if not os.path.isfile('token.txt'):  # check if token.txt exists
    print('Bot API token should be passed in token.txt file', file=sys.stderr)
    exit(1)

with open('token.txt') as tk:  # attempt to read api token
    bot = telebot.TeleBot(tk.read().strip())


menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)  # this markup is bot menu
menu.add(KeyboardButton('/logic'))
menu.add(KeyboardButton('/det'))
menu.add(KeyboardButton('/idempotents'))
menu.add(KeyboardButton('/nilpotents'))
menu.add(KeyboardButton('/inverse'))
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
                     ('/det для нахождения определителя матрицы (не более чем 8x8).\n'
                      '/logic для построения таблицы истинности логического выражения.\n'
                      '/idempotents для поиска идемпотентных элементов в Z/n.\n'
                      '/nilpotents для поиска нильпотентных элементов в Z/n.\n'
                      '/inverse для поиска обратного элемента в Z/n.\n\n'
                      '<u>Описание допустимых логических операторов</u>\n'
                      f'{ops_description}'),
                     parse_mode='html')


@bot.message_handler(commands=['det'])
def det(message):
    m = bot.send_message(message.chat.id, 'Введите матрицу: (одним сообщением)', reply_markup=hide_menu)
    bot.register_next_step_handler(m, matrix_input, action='det')


def calc_det(message, action, matrix):
    try:
        answer = matrix.det()
    except SquareMatrixRequired:
        bot.reply_to(message, 'Невозможно рассчитать определитель для не квадратной матрицы!', reply_markup=menu)
    else:
        bot.reply_to(message, f'{answer}', reply_markup=menu)


action_mapper = {
    'det': calc_det
}


def matrix_input(message, action):
    try:
        lst = [[float(x) for x in row.split()] for row in message.text.split('\n')]
        matrix = Matrix.from_list(lst)
    except SizesMatchError:
        bot.reply_to(message,
                     'Несовпадение размеров строк или столбцов. Матрица должна быть <b>прямоугольной</b>.',
                     reply_markup=menu,
                     parse_mode='html')
    except ValueError:
        bot.reply_to(message,
                     'Необходимо вводить <b>числовую</b> квадратную матрицу',
                     reply_markup=menu,
                     parse_mode='html')
    else:
        next_handler = action_mapper[action]
        next_handler(message, action=action, matrix=matrix)


@bot.message_handler(commands=['logic'])
def logic_input(message):
    m = bot.send_message(message.chat.id, 'Введите логическое выражение:', reply_markup=hide_menu)
    bot.register_next_step_handler(m, logic_output)


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


@bot.message_handler(commands=['idempotents', 'nilpotents'])
def ring_input(message):
    m = bot.send_message(message.chat.id, 'Введите модуль кольца:')
    bot.register_next_step_handler(m, ring_output, command=message.text[1:])


def ring_output(message, command):
    try:
        n = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка ввода данных', reply_markup=menu)
        return
    if n >= MAX_MODULO or n < 2:
        bot.send_message(message.chat.id, f'Ограничение: 2 <= n < {MAX_MODULO:E}', reply_markup=menu)
        return
    if command == 'idempotents':
        result = find_idempotents(n)
        title = 'Идемпотенты'
    elif command == 'nilpotents':
        result = find_nilpotents(n)
        title = 'Нильпотенты'
    else:
        return
    s = '\n'.join([str(x) for x in result])
    bot.send_message(message.chat.id,
                     f'<b> {title} в Z/{n}</b>\n'
                     f'Количество: {len(result)}\n\n'
                     f'{s}\n',
                     reply_markup=menu,
                     parse_mode='html')


@bot.message_handler(commands=['inverse'])
def inverse_input_ring(message):
    m = bot.send_message(message.chat.id, 'Введите модуль кольца:')
    bot.register_next_step_handler(m, inverse_input_element)


def inverse_input_element(message):
    try:
        n = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка ввода данных', reply_markup=menu)
        return
    if n >= MAX_MODULO or n < 2:
        bot.send_message(message.chat.id, f'Ограничение: 2 <= n < {MAX_MODULO:E}', reply_markup=menu)
        return
    m = bot.send_message(message.chat.id, 'Введите элемент, для которого требуется найти обратный:')
    bot.register_next_step_handler(m, inverse_output, modulo=n)


def inverse_output(message, modulo):
    try:
        n = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка ввода данных', reply_markup=menu)
        return
    n = n % modulo
    try:
        result = find_inverse(n, modulo)
    except ArithmeticError:
        bot.send_message(
            message.chat.id,
            f'У {n} <b>нет</b> обратного в кольце Z/{modulo}\n'
            f'Так как НОД({n}, {modulo}) > 1',
            parse_mode='html'
        )
    else:
        bot.send_message(message.chat.id, f'{result}')


if __name__ == '__main__':
    print("Copyright (C) 2021 Ilya Bezrukov")
    print("Licensed under GNU GPL-2.0-or-later")
    bot.polling(none_stop=True)
