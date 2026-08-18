"""Small numeric helpers shared across the server."""
from numbers import Real
from typing import Iterable


def sum_even_numbers(numbers: Iterable[Real]) -> Real:
    """Return the sum of the even numbers in ``numbers``.

    A value counts as even when it is an integral number divisible by 2, so
    floats such as ``4.0`` are included while ``4.5`` is not. Booleans are
    ignored because ``True``/``False`` are not meaningful numbers here.

    Args:
        numbers: Any iterable of numeric values.

    Returns:
        The sum of the even values, or ``0`` when none are found.

    Raises:
        TypeError: If an element is not a real number.
    """
    total = 0
    for value in numbers:
        if isinstance(value, bool) or not isinstance(value, Real):
            raise TypeError(f"Expected a real number, got {value!r}")
        if value % 2 == 0:
            total += value
    return total


if __name__ == "__main__":
    print(sum_even_numbers([1, 2, 3, 4, 5, 6]))  # 12
