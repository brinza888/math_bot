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

import io

from math_bot import bot, log_function_call
from math_bot.markup import *
from math_bot.core.logic import build_table
from math_bot.core import shunting_yard as sy


@bot.message_handler(commands=["logic"])
def logic_input(message):
    m = bot.send_message(message.chat.id, "Введите логическое выражение:",  # TODO: make logic operators description
                         reply_markup=hide_menu,
                         parse_mode="html")
    bot.register_next_step_handler(m, logic_output)


@log_function_call("logic")
def logic_output(message):
    try:
        table, variables = build_table(message.text)
        out = io.StringIO()  # abstract file (file-object)
        print(*variables, "F", file=out, sep=" " * 2)
        for row in table:
            print(*row, file=out, sep=" " * 2)
        answer = f"<code>{out.getvalue()}</code>"
        bot.send_message(message.chat.id, answer, parse_mode="html", reply_markup=menu)
        return answer
    except sy.InvalidSyntax:
        bot.send_message(message.chat.id, "Синтаксическая ошибка в выражении", reply_markup=menu)
    except sy.InvalidName:
        bot.send_message(message.chat.id, "Встречена неизвестная переменная", reply_markup=menu)
    except sy.InvalidArguments:
        bot.send_message(message.chat.id, "Неправильное использование функции", reply_markup=menu)
    except sy.CalculationLimitError:
        bot.send_message(message.chat.id, "Достигнут лимит возможной сложности вычислений", reply_markup=menu)
    except ValueError:
        bot.send_message(message.chat.id, "Не удалось распознать значение. Допустимые: 0, 1", reply_markup=menu)
