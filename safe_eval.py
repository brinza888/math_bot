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

import math
import operator as op

from shunting_yard import ShuntingYard, Operator, Function
from shunting_yard import InvalidSyntax, InvalidName, InvalidArguments
from config import Config


class LimitError (ValueError):
    """ Base class for limit exceptions """
    pass


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
        Operator("^", op.pow, 10, assoc=Operator.Associativity.RIGHT),
    ],
    [
        # general math functions
        Function("abs", abs),
        Function("round", round),
        Function("pow", pow, argc=2),
        Function("sqrt", math.sqrt),
        Function("factorial", math.factorial),

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
        Function("exp", math.exp),
    ],
    use_variables=False,
    default_variables={
        "pi": math.pi,
        "e": math.e
    },
    converter=lambda x: float(x) if "." in x else int(x)
)


def safe_eval(expr):
    if len(expr) >= Config.CALC_LINE_LIMIT:
        raise LimitError("Expression length limit exceeded")
    pexpr = mathSY.parse(expr)
    pexpr = mathSY.shunt(pexpr)
    return pexpr.eval()


if __name__ == "__main__":
    print("Copyright (C) 2021-2022 Ilya Bezrukov, Stepan Chizhov, Artem Grishin")
    print("Licensed under GNU GPL-2.0-or-later")
    while True:
        try:
            print(safe_eval(input("> ")))
        except (InvalidSyntax, InvalidName, InvalidArguments, ArithmeticError) as ex:
            print(ex.__class__.__name__, ":", ex)
        except KeyboardInterrupt:
            print("Bye!")
            break
