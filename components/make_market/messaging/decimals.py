import functools
import math
from decimal import Decimal


def float_to_int_with_precision(value: float, exponent: int) -> tuple[int, int]:
    # normalize the value to the given exponent
    factor = Decimal(10.0) ** exponent

    # get the sign, digits, and exponent of the value
    sign, digits, exponent = Decimal(value).quantize(factor).as_tuple()

    # combine the sign and digits
    number = int("".join(map(str, digits))) * (-1 if sign else 1)

    return number, exponent


def decimal_from_int_number_with_exponent(number: int, exponent: int) -> Decimal:
    """
    Converts an integer number to a Decimal with a given exponent.

    Args:
        number (int): The integer number to be converted.
        exponent (int): The exponent to be applied to the number.

    Returns:
        Decimal: The resulting Decimal value after applying the exponent.

    """
    return Decimal(number) * Decimal(10) ** exponent
