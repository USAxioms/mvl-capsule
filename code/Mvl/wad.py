"""WAD-18: one optional deterministic fixed-point profile (not required by MVL)."""
from decimal import Decimal

Q = 10 ** 18
BOUND = 2 ** 255 - 1


class WadError(Exception):
    pass


def checked(n: int) -> int:
    if not isinstance(n, int) or isinstance(n, bool):
        raise WadError("non-integer value")
    if not -BOUND <= n <= BOUND:
        raise WadError("overflow")
    return n


def encode(text: str) -> int:
    d = Decimal(text)
    exp = d.as_tuple().exponent
    if isinstance(exp, int) and exp < -18:
        raise WadError("excess precision")
    return checked(int(d * Q))


def add(a: int, b: int) -> int:
    return checked(checked(a) + checked(b))


def mul(a: int, b: int) -> int:
    p = checked(a) * checked(b)
    if p % Q:
        raise WadError("non-exact multiplication")
    return checked(p // Q)


def div(a: int, b: int) -> int:
    if b == 0:
        raise WadError("division by zero")
    n = checked(a) * Q
    if n % b:
        raise WadError("non-exact division")
    return checked(n // b)
