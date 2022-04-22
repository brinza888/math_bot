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

from collections import deque


OPS = {
    '~': (0, 1, lambda x: not x, 'Отрицание (НЕ)'),
    '&': (1, 2, lambda x, y: x and y, 'Конъюнкция (И)'),
    '|': (2, 2, lambda x, y: x or y, 'Дизъюнкция (ИЛИ)'),
    '>': (3, 2, lambda x, y: not x or y, 'Импликация (следовательно)'),
    '^': (4, 2, lambda x, y: x != y, 'Исключающее ИЛИ (XOR)'),
    '=': (4, 2, lambda x, y: x == y, 'Эквиваленция (тождество)')
}


def shunting_yard(s):
    variables = []
    right = deque(s.replace(' ', ''))
    stack = []
    out = []
    while right:
        t = right.popleft()
        if t in variables:
            out.append(t)
        elif t.isdigit():
            out.append(bool(t))
        elif t in OPS:
            while len(stack) > 0 and stack[-1] in OPS and OPS[stack[-1]][0] <= OPS[t][0]:
                out.append(stack.pop())
            stack.append(t)
        elif t == '(':
            stack.append(t)
        elif t == ')':
            while stack[-1] != '(':
                out.append(stack.pop())
            stack.pop()
        else:
            if t not in variables:
                variables.append(t)
            out.append(t)
    while stack:
        out.append(stack.pop())
    return out, variables


def calculate(tokens, variables):
    stack = []
    for t in tokens:
        if t in OPS:
            operands = deque()
            for i in range(OPS[t][1]):
                if len(stack) == 0:
                    raise SyntaxError('Incorrect logic expression')
                operands.appendleft(stack.pop())
            stack.append(OPS[t][2](*operands))
        elif t.isalpha():
            if t in variables:
                stack.append(bool(variables[t]))
            else:
                raise NameError(f'Variable "{t}" not defined!')
        else:
            stack.append(t)

    if not stack or len(stack) > 1:
        raise SyntaxError('Incorrect logic expression')
    return stack[-1]


def build_table(s, var_limit=8):
    tokens, variables = shunting_yard(s)  # kowalski analysis
    n = len(variables)
    if n > var_limit:
        raise ValueError("Variables limit reached")
    table = []
    for i in range(2 ** n):
        values = [int(x) for x in bin(i)[2:].rjust(n, '0')]
        d = {variables[k]: values[k] for k in range(n)}
        table.append(values + [int(calculate(tokens, d))])
    return table, variables


if __name__ == '__main__':
    print("Copyright (C) 2021-2022 Ilya Bezrukov, Stepan Chizhov, Artem Grishin")
    print("Licensed under GNU GPL-2.0-or-later")
    s = input('Expression: ')
    table, variables = build_table(s)
    print(*variables, 'F')
    for row in table:
        print(*row)
