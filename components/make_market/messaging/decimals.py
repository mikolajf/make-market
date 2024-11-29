from decimal import Decimal


def float_to_digits_with_precision(value: float, exponent: int) -> int:
    """
    Converts a floating-point number to an integer digits with a specified precision.

    Args:
        value (float): The floating-point number to convert.
        exponent (int): The number of decimal places to consider for the conversion.

    Returns:
        int: The integer representation of the floating-point number with the specified precision.

    """
    # normalize the value to the given exponent
    factor = Decimal(10.0) ** exponent

    # get the sign, digits, and exponent of the value
    sign, digits, exponent = Decimal(value).quantize(factor).as_tuple()

    # combine the sign and digits
    return int("".join(map(str, digits))) * (-1 if sign else 1)


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
