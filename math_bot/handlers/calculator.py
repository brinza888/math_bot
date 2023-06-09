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
from math_bot.core.safe_eval import safe_eval
from math_bot.core import shunting_yard as sy


@bot.message_handler(commands=["calc"])
def calc_input(message):
    m = bot.send_message(message.chat.id, "Введите выражение:", parse_mode="html")
    bot.register_next_step_handler(m, calc_output)


@log_function_call("calc")
def calc_output(message):
    try:
        answer = str(safe_eval(message.text))
    except sy.InvalidSyntax:
        bot.send_message(message.chat.id, "Синтаксическая ошибка в выражении", reply_markup=menu)
    except sy.InvalidName:
        bot.send_message(message.chat.id, "Встречена неизвестная переменная", reply_markup=menu)
    except sy.InvalidArguments:
        bot.send_message(message.chat.id, "Неправильное использование функции")
    except sy.CalculationLimitError:
        bot.send_message(message.chat.id, "Достигнут лимит возможной сложности вычислений", reply_markup=menu)
    except ZeroDivisionError:
        bot.send_message(message.chat.id, "Во время выполнения встречено деление на 0", reply_markup=menu)
    except ArithmeticError:
        bot.send_message(message.chat.id, "Арифметическая ошибка", reply_markup=menu)
    except ValueError:
        bot.send_message(message.chat.id, "Не удалось распознать значение", reply_markup=menu)
    else:
        bot.send_message(message.chat.id, answer, parse_mode="html", reply_markup=menu)
        return answer
