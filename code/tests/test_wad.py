import random
import unittest
from decimal import Decimal, getcontext

from mvl.wad import Q, BOUND, WadError, encode, add, mul, div

getcontext().prec = 200


class Wad(unittest.TestCase):
    def test_paper_example(self):
        self.assertEqual(add(encode("1000.10"), encode("0.20")), encode("1000.30"))

    def test_refusals(self):
        with self.assertRaises(WadError):
            encode("0." + "1" * 19)
        with self.assertRaises(WadError):
            div(Q, 0)
        with self.assertRaises(WadError):
            div(10 * Q, 3 * Q)
        with self.assertRaises(WadError):
            mul(1, Q // 2)
        with self.assertRaises(WadError):
            add(BOUND, 1)

    def test_random_against_decimal(self):
        rng = random.Random(18)
        for _ in range(2000):
            a = Decimal(rng.randint(-10**9, 10**9)) / 100
            b = Decimal(rng.randint(-10**9, 10**9)) / 100
            na, nb = encode(str(a)), encode(str(b))
            self.assertEqual(Decimal(add(na, nb)) / Q, a + b)
            try:
                self.assertEqual(Decimal(mul(na, nb)) / Q, a * b)
            except WadError:
                self.assertNotEqual((na * nb) % Q, 0)
            if b != 0:
                try:
                    self.assertEqual(Decimal(div(na, nb)) / Q, a / b)
                except WadError:
                    self.assertNotEqual((na * Q) % nb, 0)


if __name__ == "__main__":
    unittest.main()
