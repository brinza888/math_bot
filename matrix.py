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

from typing import Tuple, List, Union
from functools import lru_cache
from fractions import Fraction
import hashlib


class SizesMatchError (ValueError):
    pass


class NonInvertibleMatrix (ValueError):
    pass


class SquareMatrixRequired (ValueError):
    pass


MatrixNumber = Union[float, int, Fraction]


class Matrix:
    def __init__(self, m: int, n: int, initial: MatrixNumber = 0):
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

    def __getitem__(self, item: Tuple[int, int]) -> MatrixNumber:
        return self.matrix[item[0]][item[1]]

    def __setitem__(self, key: Tuple[int, int], value: MatrixNumber):
        self.matrix[key[0]][key[1]] = float(value)

    def __eq__(self, other: "Matrix") -> bool:
        if self.size != other.size:
            return False
        for i in range(self.m):
            for j in range(self.n):
                if self[i, j] != other[i, j]:
                    return False
        return True

    def __hash__(self) -> int:  # hashing for lru_cache decorator
        result = f"{self.m};{self.n};"
        for row in self.matrix:
            result += ",".join([str(x) for x in row]) + ";"
        return int.from_bytes(hashlib.sha256(result.encode()).digest(), "little")

    def __repr__(self) -> str:
        return "\n".join([
            "\t".join([f"{x:6.3f}" for x in row])
            for row in self.matrix
        ])

    def __or__(self, other) -> "Matrix":  # vertical concatenation
        if other.m != self.m:
            raise SizesMatchError("Vertical concatenation works with same rows count")
        new_matrix = [[] for _ in range(self.m)]
        for i in range(self.m):
            new_matrix[i] = self.matrix[i] + other.matrix[i]
        new = Matrix(self.m, self.n + other.n)
        new.fill(new_matrix)
        return new

    def __xor__(self, other) -> "Matrix":  # horizontal concatenation
        if other.n != self.n:
            raise SizesMatchError("Horizontal concatenation works with same columns count")
        new_matrix = self.matrix + other.matrix
        new = Matrix(self.m + other.m, self.n)
        new.fill(new_matrix)
        return new

    def __add__(self, other: "Matrix") -> "Matrix":
        if other.size != self.size:
            raise SizesMatchError("Addition available for equal size matrices")
        result = Matrix(self.m, self.n)
        for i in range(self.m):
            for j in range(self.n):
                result[i, j] = self[i, j] + other[i, j]
        return result

    def __mul__(self, other: "Matrix") -> "Matrix":
        if self.n != other.m:
            raise SizesMatchError("Multiplication available only for matrices with size MxN and NxL")
        result = Matrix(self.m, other.n)
        for i in range(result.m):
            for j in range(result.n):
                for k in range(self.n):
                    result[i, j] += self[i, k] * other[k, j]
        return result

    def copy(self) -> "Matrix":
        return Matrix.from_list(self.matrix)

    def fill(self, lst: List[List[MatrixNumber]]):
        rows = len(lst)
        if rows != self.m:
            raise SizesMatchError("Count of rows in list must be same with count of rows in Matrix")
        for i, row in enumerate(lst):
            if len(row) != self.n:
                raise SizesMatchError("Count of elements in list row must be same with count of columns in Matrix")
            for j, element in enumerate(row):
                self.matrix[i][j] = float(element)

    def minor(self, el_i: int, el_j: int) -> "Matrix":
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
    def det(self) -> MatrixNumber:
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

    def swap_rows(self, a: int, b: int):
        for i in range(self.n):
            self.matrix[a][i], self.matrix[b][i] = self.matrix[b][i], self.matrix[a][i]

    def swap_columns(self, a: int, b: int):
        for j in range(self.m):
            self.matrix[j][a], self.matrix[j][b] = self.matrix[j][b], self.matrix[j][a]

    def ref(self) -> "Matrix":
        ref = self.copy()
        straight_gaussian(ref)
        return ref

    def inverse(self) -> "Matrix":
        if not self.is_square or self.det() == 0:
            raise NonInvertibleMatrix("Invertible matrix must be square with non-zero determinant")
        tmp = self.copy()
        inverse = straight_gaussian(tmp, Matrix.identity(self.n))
        inverse = reverse_gaussian(tmp, inverse)
        return inverse

    @classmethod
    def from_list(cls, lst: List[List[MatrixNumber]]) -> "Matrix":
        matrix = Matrix(len(lst), len(lst[0]))
        matrix.fill(lst)
        return matrix

    @classmethod
    def row(cls, lst: List[MatrixNumber]) -> "Matrix":
        matrix = Matrix(1, len(lst))
        matrix.fill([lst])
        return matrix

    @classmethod
    def column(cls, lst: List[MatrixNumber]) -> "Matrix":
        matrix = Matrix(len(lst), 1)
        matrix.fill([[x] for x in lst])
        return matrix

    @classmethod
    def zero(cls, m: int, n: int) -> "Matrix":
        return Matrix(m, n)

    @classmethod
    def identity(cls, n: int) -> "Matrix":
        matrix = Matrix(n, n)
        for i in range(n):
            matrix.matrix[i][i] = 1
        return matrix


def straight_gaussian(matrix: Matrix, additional: Matrix = None) -> "Matrix":
    if additional is None:
        additional = Matrix.zero(matrix.m, 1)
    for k in range(matrix.n):  # Straight ahead (Lower left-hand corner jamming)
        if k >= matrix.m:
            break
        for i in range(k, matrix.m):
            for j in range(i, matrix.m):
                if (matrix[i, k] == 0 or abs(matrix[i, k]) > abs(matrix[j, k])) and matrix[j, k] != 0:
                    matrix.swap_rows(i, j)
                    additional.swap_rows(i, j)
        if matrix[k, k] == 0:  # skip if k column full in zeros
            continue
        for i in range(k + 1, matrix.m):  # Subtract k row from all lower
            leading = matrix[i, k]
            for j in range(k, matrix.n):
                matrix[i, j] -= matrix[k, j] * leading / matrix[k, k]
            for j in range(additional.n):
                additional[i, j] -= additional[k, j] * leading / matrix[k, k]
    return additional


def reverse_gaussian(matrix: Matrix, additional: Matrix = None) -> "Matrix":
    if additional is None:
        additional = Matrix.zero(matrix.m, 1)
    for k in range(matrix.m - 1, -1, -1):  # Backward (upper right-hand corner jamming)
        divider = matrix[k, k]
        for j in range(matrix.n):  # leading coefficient = 1
            matrix[k, j] = matrix[k, j] / divider
        for j in range(additional.n):
            additional[k, j] = additional[k, j] / divider
        for i in range(k - 1, -1, -1):
            leading = matrix[i, k]
            if leading == 0:
                continue
            for j in range(matrix.n - 1, -1, -1):
                matrix[i, j] -= matrix[k, j] * leading
            for j in range(additional.n - 1, -1, -1):
                additional[i, j] -= additional[k, j] * leading
    return additional


if __name__ == "__main__":
    print("Copyright (C) 2021-2023 Ilya Bezrukov, Stepan Chizhov, Artem Grishin")
    print("Licensed under GNU GPL-2.0-or-later")
    m, n = map(int, input("Введите размер матрицы: ").split())
    print("Введите матрицу: ")
    matrix = [list(map(float, input().split())) for i in range(m)]
    A = Matrix(m, n)
    A.fill(matrix)
    print(A.ref())
