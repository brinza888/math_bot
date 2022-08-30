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

from typing import Tuple, List, Union
from functools import lru_cache
import hashlib


class SizesMatchError (ValueError):
    pass


class NonInvertibleMatrix (ValueError):
    pass


class SquareMatrixRequired (ValueError):
    pass


class Matrix:
    def __init__(self, m: int, n: int, initial: Union[float, int] = 0):
        self.__size: Tuple[int, int] = (m, n)
        self.matrix = [[initial] * n for _ in range(m)]

    @property
    def m(self) -> int:
        return self.__size[0]

    @property
    def n(self) -> int:
        return self.__size[1]

    @property
    def is_square(self) -> bool:
        return self.m == self.n

    @property
    def size(self) -> Tuple[int, int]:
        return self.__size

    def __getitem__(self, item: Tuple[int, int]) -> float:
        return self.matrix[item[0]][item[1]]

    def __setitem__(self, key: Tuple[int, int], value: Union[float, int]):
        self.matrix[key[0]][key[1]] = float(value)

    def __eq__(self, other: 'Matrix'):
        if self.size != other.size:
            return False
        for i in range(self.m):
            for j in range(self.n):
                if self[i, j] != other[i, j]:
                    return False
        return True

    def __hash__(self):  # hashing for lru_cache decorator
        result = f"{self.m};{self.n};"
        for row in self.matrix:
            result += ','.join([str(x) for x in row]) + ';'
        return int.from_bytes(hashlib.sha256(result.encode()).digest(), "little")

    def __repr__(self):
        return '\n'.join([
            '\t'.join([f'{x:6.3f}' for x in row])
            for row in self.matrix
        ])

    def __or__(self, other):  # vertical concatenation
        if other.m != self.m:
            raise SizesMatchError("Vertical concatenation works with same rows count")
        new_matrix = [[] for _ in range(self.m)]
        for i in range(self.m):
            new_matrix[i] = self.matrix[i] + other.matrix[i]
        new = Matrix(self.m, self.n + other.n)
        new.fill(new_matrix)
        return new

    def __xor__(self, other):  # horizontal concatenation
        if other.n != self.n:
            raise SizesMatchError("Horizontal concatenation works with same columns count")
        new_matrix = self.matrix + other.matrix
        new = Matrix(self.m + other.m, self.n)
        new.fill(new_matrix)
        return new

    def fill(self, lst: List[List[Union[int, float]]]):
        rows = len(lst)
        if rows != self.m:
            raise SizesMatchError("Count of rows in list must be same with count of rows in Matrix")
        for i, row in enumerate(lst):
            if len(row) != self.n:
                raise SizesMatchError("Count of elements in list row must be same with count of columns in Matrix")
            for j, element in enumerate(row):
                self.matrix[i][j] = float(element)

    def minor(self, el_i: int, el_j: int) -> 'Matrix':
        minor = Matrix(self.m - 1, self.n - 1)
        mi, mj = 0, 0
        for i, row in enumerate(self.matrix):
            if i == el_i:
                continue
            for j, v in enumerate(row):
                if j == el_j:
                    continue
                minor[mi, mj] = float(v)
                mj += 1
            mi += 1
            mj = 0
        return minor

    @lru_cache
    def det(self) -> float:
        if len(self.matrix) == 1 and len(self.matrix[0]) == 1:
            return self.matrix[0][0]
        if not self.is_square:
            raise SquareMatrixRequired("Determinant defined only for square (m=n) matrix")
        det_value = 0
        sgn = 1
        for i in range(len(self.matrix)):
            det_value += self.matrix[i][0] * self.minor(i, 0).det() * sgn
            sgn = -sgn
        return det_value

    def _gaussian_elimination(self) -> Tuple['Matrix', 'Matrix']:
        id_matrix = Matrix(self.m, self.n)
        temp = Matrix.from_list(self.matrix)
        for i in range(min(temp.m, temp.n)):      # Constructing identity matrix
            id_matrix.matrix[i][i] = 1

        big_matrix = Matrix(temp.m, 2 * temp.n, 0)
        for i in range(temp.m):      # Merge of identity and initial matrix
            for j in range(temp.n):
                big_matrix.matrix[i][j] = temp.matrix[i][j]
                big_matrix.matrix[i][j + temp.n] = id_matrix.matrix[i][j]

        for k in range(min(temp.m, temp.n)):    # Straight ahead (Lower left-hand corner jamming)
            for i in range(2 * temp.n):
                if temp.matrix[k][k] == 0:
                    continue
                big_matrix.matrix[k][i] = big_matrix.matrix[k][i] / temp.matrix[k][k]
            for i in range(k + 1, temp.m):
                if big_matrix.matrix[k][k] == 0:
                    continue
                K = big_matrix.matrix[i][k] / big_matrix.matrix[k][k]
                for j in range(2 * temp.n):
                    big_matrix.matrix[i][j] = big_matrix.matrix[i][j] - big_matrix.matrix[k][j] * K
            for i in range(temp.m):
                for j in range(temp.n):
                    temp.matrix[i][j] = big_matrix.matrix[i][j]

        for k in range(min(temp.m, temp.n) - 1, -1, -1):   # Reverse stroke (Top right-hand corner jamming)
            for i in range(2 * temp.n - 1, -1, -1):
                if temp.matrix[k][k] == 0:
                    continue
                big_matrix.matrix[k][i] = big_matrix.matrix[k][i] / temp.matrix[k][k]
            for i in range(k - 1, -1, -1):
                if big_matrix.matrix[k][k] == 0:
                    continue
                K = big_matrix.matrix[i][k] / big_matrix.matrix[k][k]
                for j in range(2 * temp.n - 1, -1, -1):
                    big_matrix.matrix[i][j] = big_matrix.matrix[i][j] - big_matrix.matrix[k][j] * K

        return temp, big_matrix

    def inverse(self):
        if not self.is_square or self.det() == 0:
            raise NonInvertibleMatrix("Matrix is not invertible")
        temp, big_matrix = self._gaussian_elimination()
        for i in range(self.m):
            for j in range(self.n):
                temp.matrix[i][j] = big_matrix.matrix[i][j + self.n]
        return temp

    def ref(self):
        temp, big_matrix = self._gaussian_elimination()
        return temp

    def rref(self):
        temp, big_matrix = self._gaussian_elimination()
        for i in range(self.m):
            for j in range(self.n):
                temp.matrix[i][j] = big_matrix.matrix[i][j]
        return temp

    @classmethod
    def from_list(cls, lst: List[List[Union[int, float]]]) -> 'Matrix':
        matrix = Matrix(len(lst), len(lst[0]))
        matrix.fill(lst)
        return matrix

    @classmethod
    def row(cls, lst: List[float]) -> 'Matrix':
        matrix = Matrix(1, len(lst))
        matrix.fill([lst])
        return matrix

    @classmethod
    def column(cls, lst: List[float]) -> 'Matrix':
        matrix = Matrix(len(lst), 1)
        matrix.fill([[x] for x in lst])
        return matrix

    @classmethod
    def zero(cls, m: int, n: int) -> 'Matrix':
        return Matrix(m, n)

    @classmethod
    def identity(cls, n: int) -> 'Matrix':
        matrix = Matrix(n, n)
        for i in range(n):
            matrix.matrix[i][i] = 1
        return matrix


if __name__ == '__main__':
    print("Copyright (C) 2021-2022 Ilya Bezrukov, Stepan Chizhov, Artem Grishin")
    print("Licensed under GNU GPL-2.0-or-later")
    m, n = map(int, input('Введите размер матрицы: ').split())
    print('Введите матрицу: ')
    matrix = [list(map(float, input().split())) for i in range(m)]
    A = Matrix(m, n)
    A.fill(matrix)
    print(A.rref())
