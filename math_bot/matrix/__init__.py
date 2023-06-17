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

from math_bot.module import MBModule
from math_bot import markup

from .matrix import Matrix, SquareMatrixRequired, NonInvertibleMatrix, SizesMatchError


class MatrixModule(MBModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action_mapper = {
            "det": self.calc_det,
            "ref": self.calc_ref,
            "m_inverse": self.calc_inv
        }

    def setup(self):
        self.bot.register_message_handler(self.det, commands=["det"])
        self.bot.register_message_handler(self.ref_input, commands=["ref"])
        self.bot.register_message_handler(self.inv_input, commands=["m_inverse"])

    def det(self, message):
        m = self.bot.send_message(message.chat.id, "Введите матрицу: (одним сообщением)",
                                  reply_markup=markup.hide_menu)
        self.bot.register_next_step_handler(m, self.matrix_input, action="det")

    def calc_det(self, message, action, matrix):
        try:
            result = matrix.det()
        except SquareMatrixRequired:
            self.bot.reply_to(message, "Невозможно рассчитать определитель для не квадратной матрицы!",
                              reply_markup=markup.menu)
        else:
            answer = str(result)
            self.bot.reply_to(message, answer, reply_markup=markup.menu)
            return answer

    def ref_input(self, message):
        m = self.bot.send_message(message.chat.id, "Введите матрицу: (одним сообщением)", reply_markup=markup.hide_menu)
        self.bot.register_next_step_handler(m, self.matrix_input, action="ref")

    def calc_ref(self, message, action, matrix):
        result = matrix.ref()
        answer = f"Матрица в ступенчатом виде:\n<code>{str(result)}</code>"
        self.bot.send_message(message.chat.id, answer, reply_markup=markup.menu)
        return answer

    def inv_input(self, message):
        m = self.bot.send_message(message.chat.id, "Введите матрицу: (одним сообщением)", reply_markup=markup.hide_menu)
        self.bot.register_next_step_handler(m, self.matrix_input, action="m_inverse")

    def calc_inv(self, message, action, matrix):
        try:
            result = matrix.inverse()
        except NonInvertibleMatrix:
            self.bot.send_message(message.chat.id, "Обратной матрицы не существует!", reply_markup=markup.menu)
            return
        else:
            answer = f"Обратная матрица:\n<code>{str(result)}</code>"
            self.bot.send_message(message.chat.id, answer, reply_markup=markup.menu)
            return answer

    def matrix_input(self, message, action):
        try:
            lst = [[float(x) for x in row.split()] for row in message.text.split("\n")]
            matrix = Matrix.from_list(lst)
        except SizesMatchError:
            self.bot.reply_to(message,
                              "Несовпадение размеров строк или столбцов. Матрица должна быть <b>прямоугольной</b>.",
                              reply_markup=markup.menu)
        except ValueError:
            self.bot.reply_to(message,
                              "Необходимо вводить <b>числовую</b> квадратную матрицу",
                              reply_markup=markup.menu)
        else:
            if matrix.n > self.config.MAX_MATRIX:
                self.bot.reply_to(message,
                                  f"Ввод матрицы имеет ограничение в {self.config.MAX_MATRIX}x{self.config.MAX_MATRIX}!",
                                  reply_markup=markup.menu)
            else:
                next_handler = self.action_mapper[action]
                next_handler(message, action=action, matrix=matrix)
