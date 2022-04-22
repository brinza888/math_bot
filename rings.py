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

from typing import *
from functools import reduce, lru_cache
from math import gcd
from itertools import product


def ext_gcd(a, b):
    """
    Calculate GCD(a, b) and solve Diofant equation ax + by = 1
    :param a: value for coefficient a
    :param b: value for coefficient b
    :return: tuple with GCD, x, y
    """
    if a == 0:
        return b, 0, 1
    d, x0, y0 = ext_gcd(b % a, a)
    x = y0 - (b // a) * x0
    y = x0
    return d, x, y


@lru_cache
def factorize(n: int) -> Dict[int, int]:
    """
    Factorize number in product of prime numbers
    :param n: number
    :return: factorization in dict of (p, k), where p - prime number, k - it's power.
    """
    d = 2
    primes = {}
    while n > 1:
        if n % d == 0:
            primes[d] = primes.get(d, 0) + 1
            n //= d
        elif d * d > n:
            d = n
        else:
            d += 1
    return primes


def defactorize(factorization: Dict[int, int]) -> int:
    """
    Build integer number from it's factorization
    :param factorization: number representation in product of prime powers
    :return: integer equivalent for factorization
    """
    n = 1
    for k, v in factorization.items():
        n *= k ** v
    return n


def factorize_str(factorization) -> str:
    """
    Make string representation for number in factorized form
    :param factorization:
    :return: string with product of primes' powers
    """
    return ' * '.join([f'{k}^{v}' for k, v in factorization.items()])


def find_inverse(a: int, n: int) -> int:
    """
    Find modular inverse for a by modulo n. ArithmeticError is raised if inverse not exists.
    :param a: reversible element
    :param n: ring modulo
    :return: modular inverse
    """
    d, ia, y = ext_gcd(a, n)
    if d != 1:
        raise ArithmeticError(f"GCD({a}, {n}) != 1. Modular inverse not exists!")
    return ia % n


def solve_comparisons(comparisons: Dict[int, int]):
    """
    Solve comparisons with Chinese remainder theorem.
    :param comparisons: dict with pairs modulo: reminder
    :return: tuple of the least answer for comparisons and modules product
    """
    modules_gcd = reduce(gcd, comparisons.keys())
    if modules_gcd != 1 and len(comparisons) != 1:
        raise ArithmeticError("Modules must be relative prime numbers!")
    modules_product = reduce(lambda _a, _b: _a * _b, comparisons.keys())
    partial_products = [modules_product // x for x in comparisons.keys()]
    z = 0
    for x, pp, m in zip(comparisons.values(), partial_products, comparisons.keys()):
        z += x * pp * find_inverse(pp, m)
    return z % modules_product, modules_product


def find_nilpotents(n: int) -> list:
    """
    Find all nilpotents in ring of modulo n
    :param n: ring modulo
    :return: list of all nilpotent elements
    """
    result = []
    fn = factorize(n)
    np = defactorize({k: 1 for k, v in fn.items()})
    count = n // np
    for i in range(count):
        result.append(np * i)
    return result


def find_idempotents(n: int) -> list:
    """
    Find all idempotents in ring of modulo n
    :param n: ring modulo
    :return: list of all idempotent elements
    """
    result = []
    fn = factorize(n)
    factored_rings = []
    for p, k in fn.items():
        factored_rings.append(p ** k)
    rings_count = len(factored_rings)
    for element in product((0, 1), repeat=rings_count):
        e, _ = solve_comparisons({modulo: reminder for modulo, reminder in zip(factored_rings, element)})
        result.append((element, e))
    return result


if __name__ == '__main__':
    print("Copyright (C) 2021-2022 Ilya Bezrukov, Stepan Chizhov, Artem Grishin")
    print("Licensed under GNU GPL-2.0-or-later")
    a, n = map(int, input("Элемент и модуль кольца: ").split())
    try:
        print(f"Обратный к {a}:", find_inverse(a, n))
    except ArithmeticError:
        print(f"Обратного к {a} в кольце Z/{n} не существует!")
