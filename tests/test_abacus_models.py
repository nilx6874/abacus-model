import unittest

from abacus.abacus_models import Abacus, BiQuinaryRod, modify_displayed_list


class BiQuinaryRodTests(unittest.TestCase):
    def test_all_decimal_digits_round_trip(self):
        for value in range(10):
            with self.subTest(value=value):
                rod = BiQuinaryRod()
                rod.set_value(value)
                self.assertEqual(value, rod.value())

    def test_set_value_rejects_values_outside_a_decimal_digit(self):
        for value in (-1, 10, 14):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    BiQuinaryRod().set_value(value)

    def test_set_value_rejects_non_integer_values(self):
        for value in (1.5, "1", True):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    BiQuinaryRod().set_value(value)

    def test_display_transformation_preserves_seven_integer_positions(self):
        for value in range(10):
            with self.subTest(value=value):
                rod = BiQuinaryRod()
                rod.set_value(value)
                displayed = modify_displayed_list(rod.display())

                quinary_value = value % 5
                expected = (
                    ([1, 0] if value < 5 else [0, 1])
                    + [1] * quinary_value
                    + [0]
                    + [1] * (4 - quinary_value)
                )
                self.assertEqual(expected, displayed)
                self.assertTrue(all(type(position) is int for position in displayed))


class AbacusTests(unittest.TestCase):
    def test_add_and_subtract_exhaustively_for_two_rods(self):
        for start in range(100):
            for operand in range(100 - start):
                abacus = Abacus(2)
                abacus.add(start)
                abacus.add(operand)
                self.assertEqual(start + operand, abacus.current_value())

            for operand in range(start + 1):
                abacus = Abacus(2)
                abacus.add(start)
                abacus.subtract(operand)
                self.assertEqual(start - operand, abacus.current_value())

    def test_add_rejects_overflow_without_changing_value(self):
        abacus = Abacus(2)
        abacus.add(99)

        with self.assertRaises(ValueError):
            abacus.add(1)

        self.assertEqual(99, abacus.current_value())

    def test_subtract_rejects_underflow_without_changing_value(self):
        abacus = Abacus(2)
        abacus.add(5)

        with self.assertRaises(ValueError):
            abacus.subtract(6)

        self.assertEqual(5, abacus.current_value())

    def test_operations_reject_negative_operands(self):
        for method_name in ("add", "subtract"):
            with self.subTest(method=method_name):
                abacus = Abacus(2)
                with self.assertRaises(ValueError):
                    getattr(abacus, method_name)(-1)
                self.assertEqual(0, abacus.current_value())

    def test_operations_reject_non_integer_operands(self):
        for method_name in ("add", "subtract"):
            for operand in (1.5, "1", True):
                with self.subTest(method=method_name, operand=operand):
                    with self.assertRaises(TypeError):
                        getattr(Abacus(2), method_name)(operand)

    def test_constructor_rejects_invalid_number_of_rods(self):
        for rods in (0, -1):
            with self.subTest(rods=rods):
                with self.assertRaises(ValueError):
                    Abacus(rods)

        for rods in (1.5, "2", True):
            with self.subTest(rods=rods):
                with self.assertRaises(TypeError):
                    Abacus(rods)

    def test_full_display_renders_rods_from_top_to_bottom(self):
        abacus = Abacus(2)
        abacus.add(9)

        expected = """\
┌─────┬─────┐
│  ●  │  │  │
│  │  │  ●  │
╞═════╪═════╡
│  │  │  ●  │
│  ●  │  ●  │
│  ●  │  ●  │
│  ●  │  ●  │
│  ●  │  │  │
└─────┴─────┘
   0     9   """
        self.assertEqual(expected, abacus.display(compact=False))


if __name__ == "__main__":
    unittest.main()
