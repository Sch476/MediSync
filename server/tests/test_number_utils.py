"""Tests for server.utils.number_utils.

Run from the repository root:

    python3 -m unittest server.tests.test_number_utils -v
"""
import unittest
from decimal import Decimal
from fractions import Fraction

from server.utils.number_utils import sum_even_numbers


class SumEvenNumbersTest(unittest.TestCase):
    """Happy-path behaviour."""

    def test_sums_only_even_values(self):
        self.assertEqual(sum_even_numbers([1, 2, 3, 4, 5, 6]), 12)

    def test_empty_list_returns_zero(self):
        self.assertEqual(sum_even_numbers([]), 0)

    def test_no_even_values_returns_zero(self):
        self.assertEqual(sum_even_numbers([1, 3, 5]), 0)

    def test_handles_negative_and_zero(self):
        self.assertEqual(sum_even_numbers([-4, -3, 0, 7]), -4)

    def test_integral_floats_count_as_even(self):
        self.assertEqual(sum_even_numbers([8.0, 3.0]), 8.0)

    def test_accepts_decimal_and_fraction(self):
        self.assertEqual(sum_even_numbers([Decimal("2"), Decimal("3")]), 2)
        self.assertEqual(sum_even_numbers([Fraction(4, 1), Fraction(3, 1)]), 4)

    def test_accepts_any_iterable(self):
        self.assertEqual(sum_even_numbers(n for n in [2, 4, 5]), 6)
        self.assertEqual(sum_even_numbers((2, 4, 5)), 6)
        self.assertEqual(sum_even_numbers({2, 4, 5}), 6)

    def test_large_values(self):
        self.assertEqual(sum_even_numbers([10**20, 10**20 + 1]), 10**20)


class ValidationTest(unittest.TestCase):
    """Rejection of values the function cannot sum."""

    def test_non_numeric_element_raises_type_error(self):
        for bad in ["x", None, [2], {}, object()]:
            with self.subTest(bad=bad):
                with self.assertRaises(TypeError):
                    sum_even_numbers([2, bad])

    def test_bool_is_rejected(self):
        # bool subclasses int, so this would otherwise sum silently.
        with self.assertRaises(TypeError):
            sum_even_numbers([True, 2])

    def test_non_integer_number_raises_value_error(self):
        for bad in [4.5, Decimal("4.5"), Fraction(9, 2)]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    sum_even_numbers([2, bad])

    def test_nan_and_infinity_raise_value_error(self):
        for bad in [float("nan"), float("inf"), float("-inf")]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    sum_even_numbers([2, bad])

    def test_error_message_reports_index_and_value(self):
        with self.assertRaises(TypeError) as ctx:
            sum_even_numbers([2, 4, "x"])
        self.assertIn("index 2", str(ctx.exception))
        self.assertIn("'x'", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            sum_even_numbers([2, 4.5])
        self.assertIn("index 1", str(ctx.exception))
        self.assertIn("4.5", str(ctx.exception))

    def test_non_iterable_input_raises_type_error(self):
        for bad in [42, None, 3.5]:
            with self.subTest(bad=bad):
                with self.assertRaises(TypeError):
                    sum_even_numbers(bad)

    def test_string_input_is_rejected(self):
        # "246" is iterable, but iterating it yields characters, not numbers.
        with self.assertRaises(TypeError):
            sum_even_numbers("246")
        with self.assertRaises(TypeError):
            sum_even_numbers(b"246")


class SkipInvalidTest(unittest.TestCase):
    """Opt-in lenient mode."""

    def test_skips_invalid_elements(self):
        self.assertEqual(sum_even_numbers([2, "x", 4.5, None, 4], skip_invalid=True), 6)

    def test_all_invalid_returns_zero(self):
        self.assertEqual(sum_even_numbers(["x", None], skip_invalid=True), 0)

    def test_does_not_skip_non_iterable_input(self):
        # skip_invalid is about elements, not about the argument itself.
        with self.assertRaises(TypeError):
            sum_even_numbers(42, skip_invalid=True)

    def test_flag_is_keyword_only(self):
        with self.assertRaises(TypeError):
            sum_even_numbers([2], True)


if __name__ == "__main__":
    unittest.main()
