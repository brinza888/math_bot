# -*- coding: utf-8 -*-

# Copyright (C) 2021-2023 Ilya Bezrukov, Stepan Chizhov, Artem Grishin
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

from math_bot import bot, log_function_call
from math_bot.markup import *
from math_bot.config import Config
from math_bot.core.numbers import *


@bot.message_handler(commands=["idempotents", "nilpotents"])
def ring_input(message):
    m = bot.send_message(message.chat.id, "Введите модуль кольца:")
    bot.register_next_step_handler(m, ring_output, command=message.text[1:])


@log_function_call("ring")
def ring_output(message, command):
    try:
        n = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка ввода данных", reply_markup=menu)
        return
    if n >= Config.MAX_MODULO or n < 2:
        bot.send_message(message.chat.id, f"Ограничение: 2 <= n < {Config.MAX_MODULO:E}", reply_markup=menu)
        return
    if command == "idempotents":
        result = [f"{row} -> {el}" for row, el in find_idempotents(n)]
        title = "Идемпотенты"
    elif command == "nilpotents":
        result = find_nilpotents(n)
        title = "Нильпотенты"
    else:
        return
    if len(result) > Config.MAX_ELEMENTS:
        s = "Элементов слишком много чтобы их вывести..."
    else:
        s = "\n".join([str(x) for x in result])
    answer = (f"<b> {title} в Z/{n}</b>\n"
              f"Количество: {len(result)}\n\n"
              f"{s}\n")
    bot.send_message(
        message.chat.id,
        answer,
        reply_markup=menu,
        parse_mode="html"
    )
    return answer


@bot.message_handler(commands=["inverse"])
def inverse_input_ring(message):
    m = bot.send_message(message.chat.id, "Введите модуль кольца:")
    bot.register_next_step_handler(m, inverse_input_element)


def inverse_input_element(message):
    try:
        n = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка ввода данных", reply_markup=menu)
        return
    if n >= Config.MAX_MODULO or n < 2:
        bot.send_message(message.chat.id, f"Ограничение: 2 <= n < {Config.MAX_MODULO:E}", reply_markup=menu)
        return
    m = bot.send_message(message.chat.id, "Введите элемент, для которого требуется найти обратный:")
    bot.register_next_step_handler(m, inverse_output, modulo=n)


@log_function_call("inverse")
def inverse_output(message, modulo):
    try:
        n = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка ввода данных", reply_markup=menu)
        return
    n = n % modulo
    try:
        result = find_inverse(n, modulo)
    except ArithmeticError:
        answer = (f"У {n} <b>нет</b> обратного в кольце Z/{modulo}\n"
                  f"Так как НОД({n}, {modulo}) > 1")
        bot.send_message(message.chat.id, answer, parse_mode="html")
        return answer
    else:
        answer = str(result)
        bot.send_message(message.chat.id, answer)
        return answer


@bot.message_handler(commands=["factorize"])
def factorize_input(message):
    m = bot.send_message(message.chat.id, "Введите число:")
    bot.register_next_step_handler(m, factorize_output)


@log_function_call("factorize")
def factorize_output(message):
    try:
        n = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка ввода данных", reply_markup=menu)
        return
    if n < 2 or n > Config.FACTORIZE_MAX:
        bot.send_message(
            message.chat.id,
            f"Разложение доступно для положительных целых чисел n: 2 <= n <= {Config.FACTORIZE_MAX:E}"
        )
    else:
        fn = factorize(n)
        answer = f"{n} = " + factorize_str(fn)
        bot.send_message(message.chat.id, answer)
        return answer


@bot.message_handler(commands=["euclid"])
def euclid_input(message):
    m = bot.send_message(message.chat.id, "Введите два числа через пробел:")
    bot.register_next_step_handler(m, euclid_output)


@log_function_call("euclid")
def euclid_output(message):
    try:
        a, b = map(int, message.text.strip().split(" "))
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка ввода данных", reply_markup=menu)
        return
    d, x, y = ext_gcd(a, b)
    answer = (f"НОД({a}, {b}) = {d}\n\n"
              f"<u>Решение уравнения:</u>\n{a}*x + {b if b >= 0 else f'({b})'}*y <b>= {d}</b>\n"
              f"x = {x}\ny = {y}\n\n"
              f"<u>Внимание</u>\n"
              f"<b>Обращайте внимание на вид уравнения!</b>\n"
              f"Решается уравнение вида ax + by = НОД(a, b)!")
    bot.send_message(message.chat.id, answer, parse_mode="html")
    return answer