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


from shunting_yard import ShuntingYard, Operator, CalculationLimitError
from config import Config


def logic_converter(x: str):
    v = int(x)
    if v not in [0, 1]:
        raise ValueError("Constant must be a logic value: 1 (true) or 0 (false)")
    return bool(v)


logicSY = ShuntingYard(
    [
        Operator("~", lambda a: not a, 20, ary=Operator.Ary.UNARY),  # NOT
        Operator("&", lambda a, b: a and b, 10),  # AND

        Operator("|", lambda a, b: a or b, 5),  # OR
        Operator("^", lambda a, b: a != b, 5),  # XOR

        Operator(">", lambda a, b: not a or b, 2),  # IMP
        Operator("=", lambda a, b: a == b, 1),  # EQU
    ],
    [],
    use_variables=True,
    converter=logic_converter
)


def build_table(expr):
    pexpr = logicSY.parse(expr)
    logicSY.shunt(pexpr)
    variables = list(sorted(pexpr.variables))
    n = len(variables)
    if n > Config.MAX_VARS:
        raise CalculationLimitError("Variables count limit reached")
    table = []
    for i in range(2 ** n):
        values = [int(x) for x in bin(i)[2:].rjust(n, "0")]
        vars_ = {k: v for k, v in zip(variables, values)}
        table.append(values + [int(pexpr.eval(vars_))])
    return table, variables


if __name__ == "__main__":
    print("Copyright (C) 2021-2023 Ilya Bezrukov, Stepan Chizhov, Artem Grishin")
    print("Licensed under GNU GPL-2.0-or-later")
    s = input("> ")
    table, variables = build_table(s)
    print(*variables, "F")
    for row in table:
        print(*row)
