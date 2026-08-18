"""Small numeric helpers shared across the server."""
from decimal import Decimal
from numbers import Real
from typing import Iterable, Union

Number = Union[int, float, Decimal]

# Decimal is not a numbers.Real, but supports the arithmetic used below.
_NUMERIC_TYPES = (Real, Decimal)


def _validate(value: object, index: int) -> Number:
    """Validate a single element and return it as an integer-valued number.

    Raises:
        TypeError: If ``value`` is a bool or is not a real number.
        ValueError: If ``value`` is numeric but not a whole number (4.5, NaN,
            infinity).
    """
    # bool is a subclass of int, but True/False are not meaningful here.
    if isinstance(value, bool) or not isinstance(value, _NUMERIC_TYPES):
        raise TypeError(
            f"Element at index {index} is not a number: {value!r} "
            f"({type(value).__name__})"
        )
    if value % 1 != 0:
        raise ValueError(
            f"Element at index {index} is not an integer value: {value!r}"
        )
    return value


def sum_even_numbers(numbers: Iterable[object], *, skip_invalid: bool = False) -> Number:
    """Return the sum of the even numbers in ``numbers``.

    A value counts as even when it is a whole number divisible by 2, so ``4.0``
    is included while ``5`` is not.

    Args:
        numbers: Any iterable of values. Every element is validated before it
            is used.
        skip_invalid: When True, elements that fail validation are ignored
            instead of raising. Defaults to False (strict).

    Returns:
        The sum of the even values, or ``0`` when none are found.

    Raises:
        TypeError: If ``numbers`` is not an iterable (or is a string/bytes), or
            if an element is not a real number and ``skip_invalid`` is False.
        ValueError: If an element is numeric but not a whole number (4.5, NaN,
            infinity) and ``skip_invalid`` is False.
    """
    if isinstance(numbers, (str, bytes)):
        raise TypeError(f"Expected an iterable of numbers, got {type(numbers).__name__}")
    try:
        iterator = enumerate(numbers)
    except TypeError:
        raise TypeError(
            f"Expected an iterable of numbers, got {type(numbers).__name__}"
        ) from None

    total: Number = 0
    for index, value in iterator:
        try:
            number = _validate(value, index)
        except (TypeError, ValueError):
            if skip_invalid:
                continue
            raise
        if number % 2 == 0:
            total += number
    return total


if __name__ == "__main__":
    print(sum_even_numbers([1, 2, 3, 4, 5, 6]))  # 12
    print(sum_even_numbers([2, "x", 4.5, 4], skip_invalid=True))  # 6
