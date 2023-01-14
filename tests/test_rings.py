"""Test cases for functions from file rings.py
"""

import unittest
import random
from rings import factorize, defactorize


class TestFactorize(unittest.TestCase):
    def test_negatives(self):
        self.assertEqual(factorize(-21), {})
        self.assertEqual(factorize(-5), {})
        self.assertEqual(factorize(-185621), {})
        self.assertEqual(factorize(-623), {})

    def test_specific_cases(self):
        self.assertEqual(factorize(0), {})
        self.assertEqual(factorize(1), {})

    def test_primes(self):
        self.assertEqual(factorize(3), {3: 1})
        self.assertEqual(factorize(11), {11: 1})
        self.assertEqual(factorize(19), {19: 1})
        self.assertEqual(factorize(97), {97: 1})
    
    def test_big_primes(self):
        self.assertEqual(factorize(4363), {4363: 1})
        self.assertEqual(factorize(6761), {6761: 1})
        self.assertEqual(factorize(20063), {20063: 1})
        self.assertEqual(factorize(102121), {102121: 1})

    def test_non_primes(self):
        self.assertEqual(factorize(6), {2: 1, 3: 1})
        self.assertEqual(factorize(9), {3: 2})
        self.assertEqual(factorize(33), {3: 1, 11: 1})
        self.assertEqual(factorize(54), {2: 1, 3: 3})

    def test_big_non_primes(self):
        self.assertEqual(factorize(1524), {2: 2, 3: 1, 127: 1})
        self.assertEqual(factorize(175436), {2: 2, 61: 1, 719: 1})
        self.assertEqual(factorize(13026450), {2: 1, 3: 1, 5: 2, 86843: 1})
        self.assertEqual(factorize(596312), {2: 3, 131: 1, 569: 1})


class TestDefactorize(unittest.TestCase):
    def test_specific_cases(self):
        self.assertEqual(defactorize({1: 0}), 1)

    def test_auto(self):
        for _ in range(10):
            number = random.randint(1, 10**7)
            factorization = factorize(number)
            self.assertEqual(defactorize(factorization), number)
