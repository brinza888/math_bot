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
import math
import operator as op

from math_bot import bot, log_function_call
from math_bot.markup import *

from .shunting_yard import ShuntingYard, Operator, Function, Evaluator, errors


def cotan(x):
    return 1 / math.tan(x)


mathSY = ShuntingYard(
    [
        Operator("+", op.add, 1),
        Operator("-", op.sub, 1),
        Operator("*", op.mul, 2),
        Operator("/", op.truediv, 2),
        Operator(":", op.floordiv, 2),
        Operator("%", op.mod, 2),
        Operator("-", op.neg, 5, ary=Operator.Ary.UNARY),
        Operator("+", op.pos, 5, ary=Operator.Ary.UNARY),
        Operator("^", op.pow, 10, assoc=Operator.Associativity.RIGHT,
                 limiter=Evaluator.limit(Config.CALC_POW_UNION_LIMIT, Config.CALC_POW_EACH_LIMIT)),
    ],
    [
        # general math functions
        Function("abs", abs),
        Function("round", round),
        Function("pow", pow, argc=2,
                 limiter=Evaluator.limit(Config.CALC_POW_UNION_LIMIT, Config.CALC_POW_EACH_LIMIT)),
        Function("sqrt", math.sqrt),
        Function("factorial", math.factorial,
                 limiter=Evaluator.limit(Config.CALC_FACTORIAL_LIMIT, None)),

        # angular conversion functions
        Function("deg", math.degrees),
        Function("rad", math.radians),

        # trigonometric functions
        Function("sin", math.sin),
        Function("cos", math.cos),
        Function("tan", math.tan),
        Function("tg", math.tan),
        Function("cot", cotan),
        Function("ctg", cotan),
        Function("acos", math.acos),
        Function("arccos", math.acos),
        Function("asin", math.asin),
        Function("arcsin", math.asin),
        Function("atan", math.atan),
        Function("arctg", math.atan),

        # exponents and logarithms
        Function("log", math.log, argc=2),
        Function("lg", math.log10),
        Function("ln", lambda x: math.log(x)),
        Function("log2", math.log2),
        Function("exp", math.exp,
                 limiter=Evaluator.limit(Config.CALC_POW_UNION_LIMIT, Config.CALC_POW_EACH_LIMIT)),
    ],
    use_variables=False,
    default_variables={
        "pi": math.pi,
        "e": math.e
    },
    converter=lambda x: float(x) if "." in x else int(x),
    default_limiter=Evaluator.limit(None, Config.CALC_OPERAND_LIMIT)
)


def safe_eval(expr):
    if len(expr) >= Config.CALC_LINE_LIMIT:
        raise errors.CalculationLimitError("Expression length limit exceeded")
    pexpr = mathSY.parse(expr)
    pexpr = mathSY.shunt(pexpr)
    return pexpr.eval()


@bot.message_handler(commands=["calc"])
def calc_input(message):
    m = bot.send_message(message.chat.id, "Введите выражение:", parse_mode="html")
    bot.register_next_step_handler(m, calc_output)


@log_function_call("calc")
def calc_output(message):
    try:
        answer = str(safe_eval(message.text))
    except errors.InvalidSyntax:
        bot.send_message(message.chat.id, "Синтаксическая ошибка в выражении", reply_markup=menu)
    except errors.InvalidName:
        bot.send_message(message.chat.id, "Встречена неизвестная переменная", reply_markup=menu)
    except errors.InvalidArguments:
        bot.send_message(message.chat.id, "Неправильное использование функции")
    except errors.CalculationLimitError:
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
