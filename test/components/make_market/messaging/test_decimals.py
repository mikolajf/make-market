from decimal import Decimal

import pytest
from make_market.messaging.decimals import (
    decimal_from_int_number_with_exponent,
    float_to_digits_with_precision,
)


@pytest.mark.parametrize(
    ("value", "exponent", "expected"),
    [
        (1.005, -3, 1005),
        (1.234, -3, 1234),
        (0.1234, -4, 1234),
        (-1.005, -3, -1005),
        (123.456, -2, 12346),
        (0.0001, -4, 1),
        (0.000123, -6, 123),
        (-0.000123, -6, -123),
        (1000.0, 0, 1000),
        (0.0, 0, 0),
    ],
)
def test_float_to_int_with_precision(
    value: float, exponent: int, expected: int
) -> None:
    assert float_to_digits_with_precision(value, exponent) == expected


@pytest.mark.parametrize(
    ("number", "exponent", "expected"),
    [
        (1005, -3, Decimal("1.005")),
        (1234, -3, Decimal("1.234")),
        (1234, -4, Decimal("0.1234")),
        (-1005, -3, Decimal("-1.005")),
        (12346, -2, Decimal("123.46")),
        (1, -4, Decimal("0.0001")),
        (123, -6, Decimal("0.000123")),
        (-123, -6, Decimal("-0.000123")),
        (1000, 0, Decimal("1000")),
        (0, 0, Decimal("0")),
    ],
)
def test_decimal_from_int_number_with_exponent(
    number: int, exponent: int, expected: Decimal
) -> None:
    assert decimal_from_int_number_with_exponent(number, exponent) == expected
