# -*- coding: utf-8 -*-


def minor(matrix, mi, mj):
    minor = []
    for i, row in enumerate(matrix):
        if i == mi:
            continue
        minor.append([])
        for j, v in enumerate(row):
            if j == mj:
                continue
            minor[-1].append(v)
    return minor


def det(matrix):
    if len(matrix) == 1 and len(matrix[0]) == 1:
        return matrix[0][0]
    det_value = 0
    sgn = 1
    for i in range(len(matrix)):
        det_value += matrix[i][0] * det(minor(matrix, i, 0)) * sgn
        sgn = -sgn
    return det_value


def is_square(matrix):
    n = len(matrix)
    for row in matrix:
        if n != len(row):
            return False
    return True


"""n = int(input('Введите размер матрицы:'))
print('Введите матрицу:')
matrix = [list(map(float,input().split())) for i in range(n)]
print('Определитель:', det(matrix))"""
