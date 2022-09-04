# -*- coding: utf-8 -*-

# Copyright (C) 2021-2022 Ilya Bezrukov, Stepan Chizhov, Artem Grishin
#
# This file is part of math_bot.
#
# math_bot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
#
# math_bot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from io import StringIO

import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from config import *
from logic import build_table, OPS
from matrix import Matrix, SizesMatchError, SquareMatrixRequired, NonInvertibleMatrix
from rings import *
from safe_eval import safe_eval, LimitError
from statistics import log_function_call
from models import User, get_db, close_db

bot = telebot.TeleBot(Config.BOT_TOKEN)

# generate supported logic operators description
logic_ops_description = '\n'.join([f'{op} {op_data[3]}' for op, op_data in OPS.items()])

menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)  # this markup is bot menu
menu.add(KeyboardButton('/help'))

menu.add(KeyboardButton('/det'))
menu.add(KeyboardButton('/ref'))
menu.add(KeyboardButton('/m_inverse'))

menu.add(KeyboardButton('/factorize'))
menu.add(KeyboardButton('/euclid'))
menu.add(KeyboardButton('/idempotents'))
menu.add(KeyboardButton('/nilpotents'))
menu.add(KeyboardButton('/inverse'))
menu.add(KeyboardButton('/logic'))

menu.add(KeyboardButton('/calc'))

hide_menu = ReplyKeyboardRemove()  # sending this as reply_markup will close menu


@bot.message_handler(commands=['start'])
def start_message(message):
    send_mess = (f'<b>Привет, {message.from_user.first_name} {message.from_user.last_name}!</b>\n'
                 f'Используй клавиатуру или команды для вызова нужной фишки\n'
                 f'/help - вызов помощи')
    bot.send_message(message.chat.id, send_mess, parse_mode='html', reply_markup=menu)
    # User first-time creation
    db = get_db()
    User.get_or_create(db, message.from_user.id, message.from_user.last_name,
                       message.from_user.first_name, message.from_user.username)
    close_db()


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id,
                     ('<b>Работа с матрицами</b>\n'
                      '/det - определитель матрицы.\n'
                      '/ref - ступенчатый вид матрицы (верхне-треугольный).\n'
                      '/m_inverse - обратная матрица.\n'
                      '\n<b>Теория чисел и дискретная математика</b>\n'
                      '/factorize - разложение натурального числа в простые.\n'
                      '/euclid - НОД двух чисел и решение Диофантового уравнения.\n'
                      '/idempotents - идемпотентные элементы в Z/n.\n'
                      '/nilpotents - нильпотентные элементы в Z/n.\n'
                      '/inverse - обратный элемент в Z/n.\n'
                      '/logic - таблица истинности выражения.\n'
                      '\n<b>Калькуляторы</b>\n'
                      '/calc - калькулятор математических выражений.'
                      ),
                     parse_mode='html')


@bot.message_handler(commands=['det'])
def det(message):
    m = bot.send_message(message.chat.id, 'Введите матрицу: (одним сообщением)', reply_markup=hide_menu)
    bot.register_next_step_handler(m, matrix_input, action='det')


@log_function_call('det')
def calc_det(message, action, matrix):
    try:
        result = matrix.det()
    except SquareMatrixRequired:
        bot.reply_to(message, 'Невозможно рассчитать определитель для не квадратной матрицы!', reply_markup=menu)
    else:
        answer = str(result)
        bot.reply_to(message, answer, reply_markup=menu)
        return answer


@bot.message_handler(commands=['ref'])
def ref_input(message):
    m = bot.send_message(message.chat.id, 'Введите матрицу: (одним сообщением)', reply_markup=hide_menu)
    bot.register_next_step_handler(m, matrix_input, action='ref')


@log_function_call('ref')
def calc_ref(message, action, matrix):
    result = matrix.ref()
    answer = f'Матрица в ступенчатом виде:\n<code>{str(result)}</code>'
    bot.send_message(message.chat.id, answer, parse_mode='html', reply_markup=menu)
    return answer


@bot.message_handler(commands=['m_inverse'])
def inv_input(message):
    m = bot.send_message(message.chat.id, 'Введите матрицу: (одним сообщением)', reply_markup=hide_menu)
    bot.register_next_step_handler(m, matrix_input, action='m_inverse')


@log_function_call('m_inverse')
def calc_inv(message, action, matrix):
    try:
        result = matrix.inverse()
    except NonInvertibleMatrix:
        bot.send_message(message.chat.id, 'Обратной матрицы не существует!', reply_markup=menu)
        return
    else:
        answer = f'Обратная матрица:\n<code>{str(result)}</code>'
        bot.send_message(message.chat.id, answer, parse_mode='html', reply_markup=menu)
        return answer


action_mapper = {
    'det': calc_det,
    'ref': calc_ref,
    'm_inverse': calc_inv
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
        if matrix.n > Config.MAX_MATRIX:
            bot.reply_to(message, f'Ввод матрицы имеет ограничение в {Config.MAX_MATRIX}x{Config.MAX_MATRIX}!',
                         reply_markup=menu)
        else:
            next_handler = action_mapper[action]
            next_handler(message, action=action, matrix=matrix)


@bot.message_handler(commands=['logic'])
def logic_input(message):
    m = bot.send_message(message.chat.id, f'<u>Допустимые операторы:</u>\n{logic_ops_description}\n\n'
                                          'Введите логическое выражение:',
                         reply_markup=hide_menu,
                         parse_mode="html")
    bot.register_next_step_handler(m, logic_output)


@log_function_call('logic')
def logic_output(message):
    try:
        table, variables = build_table(message.text, Config.MAX_VARS)
        out = StringIO()  # abstract file (file-object)
        print(*variables, 'F', file=out, sep=' ' * 2)
        for row in table:
            print(*row, file=out, sep=' ' * 2)
        answer = f'<code>{out.getvalue()}</code>'
        bot.send_message(message.chat.id, answer, parse_mode='html', reply_markup=menu)
        return answer
    except (AttributeError, SyntaxError):
        bot.send_message(message.chat.id, "Ошибка ввода данных", reply_markup=menu)
    except ValueError:
        bot.send_message(message.chat.id, f"Ограничение по кол-ву переменных: {Config.MAX_VARS}")


@bot.message_handler(commands=['idempotents', 'nilpotents'])
def ring_input(message):
    m = bot.send_message(message.chat.id, 'Введите модуль кольца:')
    bot.register_next_step_handler(m, ring_output, command=message.text[1:])


@log_function_call('ring')
def ring_output(message, command):
    try:
        n = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка ввода данных', reply_markup=menu)
        return
    if n >= Config.MAX_MODULO or n < 2:
        bot.send_message(message.chat.id, f'Ограничение: 2 <= n < {Config.MAX_MODULO:E}', reply_markup=menu)
        return
    if command == 'idempotents':
        result = [f'{row} -> {el}' for row, el in find_idempotents(n)]
        title = 'Идемпотенты'
    elif command == 'nilpotents':
        result = find_nilpotents(n)
        title = 'Нильпотенты'
    else:
        return
    if len(result) > Config.MAX_ELEMENTS:
        s = 'Элементов слишком много чтобы их вывести...'
    else:
        s = '\n'.join([str(x) for x in result])
    answer = (f'<b> {title} в Z/{n}</b>\n'
              f'Количество: {len(result)}\n\n'
              f'{s}\n')
    bot.send_message(
        message.chat.id,
        answer,
        reply_markup=menu,
        parse_mode='html'
    )
    return answer


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
    if n >= Config.MAX_MODULO or n < 2:
        bot.send_message(message.chat.id, f'Ограничение: 2 <= n < {Config.MAX_MODULO:E}', reply_markup=menu)
        return
    m = bot.send_message(message.chat.id, 'Введите элемент, для которого требуется найти обратный:')
    bot.register_next_step_handler(m, inverse_output, modulo=n)


@log_function_call('inverse')
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
        answer = (f'У {n} <b>нет</b> обратного в кольце Z/{modulo}\n'
                  f'Так как НОД({n}, {modulo}) > 1')
        bot.send_message(message.chat.id, answer, parse_mode='html')
    else:
        answer = str(result)
        bot.send_message(message.chat.id, answer)
    finally:
        return answer


@bot.message_handler(commands=['factorize'])
def factorize_input(message):
    m = bot.send_message(message.chat.id, 'Введите число:')
    bot.register_next_step_handler(m, factorize_output)


@log_function_call('factorize')
def factorize_output(message):
    try:
        n = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка ввода данных', reply_markup=menu)
        return
    if n < 2 or n > Config.FACTORIZE_MAX:
        bot.send_message(
            message.chat.id,
            f'Разложение доступно для положительных целых чисел n: 2 <= n <= {Config.FACTORIZE_MAX:E}'
        )
    else:
        fn = factorize(n)
        answer = f'{n} = ' + factorize_str(fn)
        bot.send_message(message.chat.id, answer)
        return answer


@bot.message_handler(commands=['euclid'])
def euclid_input(message):
    m = bot.send_message(message.chat.id, 'Введите два числа через пробел:')
    bot.register_next_step_handler(m, euclid_output)


@log_function_call('euclid')
def euclid_output(message):
    try:
        a, b = map(int, message.text.strip().split(" "))
    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка ввода данных', reply_markup=menu)
        return
    d, x, y = ext_gcd(a, b)
    answer = (f'НОД({a}, {b}) = {d}\n\n'
              f'<u>Решение уравнения:</u>\n{a}*x + {b}*y <b>= {d}</b>\n'
              f'x = {x}\ny = {y}\n\n'
              f'<u>Внимание</u>\n'
              f'<b>Обращайте внимание на вид уравнения!</b>\n'
              f'Решается уравнение вида ax + by = НОД(a, b)!')
    bot.send_message(message.chat.id, answer, parse_mode='html')
    return answer


@bot.message_handler(commands=['calc'])
def calc_input(message):
    m = bot.send_message(message.chat.id, 'Операция возведения в степень обозначается <b>**</b>\n\n'
                                          'Введите выражение:',
                         parse_mode="html")
    bot.register_next_step_handler(m, calc_output)


@log_function_call('calc')
def calc_output(message):
    try:
        answer = str(safe_eval(message.text))
    except (SyntaxError, TypeError):
        bot.send_message(message.chat.id, 'Синтаксическая ошибка в выражении', reply_markup=menu)
    except LimitError:
        bot.send_message(message.chat.id, 'Достигнут лимит возможной сложности вычислений', reply_markup=menu)
    except ZeroDivisionError:
        bot.send_message(message.chat.id, 'Деление на 0 не определено')
    except ArithmeticError:
        bot.send_message(message.chat.id, 'Арифметическая ошибка')
    else:
        bot.send_message(message.chat.id, answer, parse_mode='html')
        return answer


@bot.message_handler(commands=["broadcast", "bc"])
def broadcast_input(message):
    if message.from_user.id not in Config.ADMINS:
        return
    m = bot.send_message(message.chat.id, "Сообщение для рассылки:")
    bot.register_next_step_handler(m, broadcast)


def broadcast(message):
    db = get_db()
    for user in db.query(User).all():
        bot.send_message(user.id, message.text)
    close_db()


if __name__ == '__main__':
    print("Copyright (C) 2021-2022 Ilya Bezrukov, Stepan Chizhov, Artem Grishin")
    print("Licensed under GNU GPL-2.0-or-later")
    bot.polling(none_stop=True)
