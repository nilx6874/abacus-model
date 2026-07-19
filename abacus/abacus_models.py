#!/usr/bin/env python
# -*- coding: utf-8 -*-

class BiQuinaryRod:
    def __init__(self):
        self.quinary = [0] * 5  # Five spots for beads, representing 1-4
        self.binary = [0] * 2  # Two spots for beads, representing 0 or 5

    # New method to get the total value of the rod
    def value(self):
        return sum(self.quinary) + (5 if self.binary[1] else 0)

    # New method to set the value of the rod
    def set_value(self, value):
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError("Rod value must be an integer")
        if not 0 <= value <= 9:
            raise ValueError("Rod value must be between 0 and 9")

        self.binary[1] = 1 if value >= 5 else 0
        self.quinary = [1 if i < value % 5 else 0 for i in range(5)]

    def display(self):
        return self.binary + self.quinary


def modify_displayed_list(lst_original):
    value = sum(lst_original[2:]) + (5 if lst_original[1] else 0)

    # Rows are returned in their console order, from top to bottom. The first
    # lower row is therefore the position closest to the separator beam.
    upper = [1, 0] if value < 5 else [0, 1]
    active_lower_beads = value % 5
    lower = (
        [1] * active_lower_beads
        + [0]
        + [1] * (4 - active_lower_beads)
    )
    return upper + lower


class Abacus:
    def __init__(self, rods=10):
        if not isinstance(rods, int) or isinstance(rods, bool):
            raise TypeError("Number of rods must be an integer")
        if rods <= 0:
            raise ValueError("Number of rods must be greater than zero")

        self.rods = [BiQuinaryRod() for _ in range(rods)]
        self.max_value = 10 ** rods - 1

    @staticmethod
    def _validate_operand(number):
        if not isinstance(number, int) or isinstance(number, bool):
            raise TypeError("Operand must be an integer")
        if number < 0:
            raise ValueError("Operand must be non-negative")

    def current_value(self):
        total = 0
        for i, rod in enumerate(self.rods):
            total += rod.value() * (10 ** i)
        return total

    def add(self, number):
        self._validate_operand(number)
        if self.current_value() + number > self.max_value:
            raise ValueError("Adding error: Number too large to be represented")

        digits = []
        while number:
            digits.append(number % 10)
            number //= 10
        self._add_digits_at_offset(digits or [0], offset=0)

    def subtract(self, number):
        self._validate_operand(number)
        if number > self.current_value():
            raise ValueError("Subtraction error: Number too large to subtract")

        borrow = 0
        for i in range(len(self.rods)):
            # Adjust digit with current borrow
            digit = (number % 10) + borrow
            number //= 10

            # Calculate the new value considering borrow
            new_value = self.rods[i].value() - digit

            # If new value is negative, set borrow for the next rod
            if new_value < 0 and i < len(self.rods) - 1:
                borrow = 1
                new_value += 10  # Adjust new value after borrowing
            else:
                borrow = 0

            self.rods[i].set_value(new_value)

            # Break if no more number to subtract and no borrow
            if number == 0 and borrow == 0:
                break

    def _copy_value_from(self, other):
        for rod, other_rod in zip(self.rods, other.rods):
            rod.set_value(other_rod.value())

    def _add_digits_at_offset(self, digits, offset):
        """Add little-endian decimal digits starting at the given rod."""
        carry = 0
        for source_index, digit in enumerate(digits):
            target_index = source_index + offset
            if target_index >= len(self.rods):
                if digit or carry:
                    raise ValueError("Number too large to be represented")
                continue

            new_value = self.rods[target_index].value() + digit + carry
            carry = new_value // 10
            self.rods[target_index].set_value(new_value % 10)

        target_index = len(digits) + offset
        while carry:
            if target_index >= len(self.rods):
                raise ValueError("Number too large to be represented")

            new_value = self.rods[target_index].value() + carry
            carry = new_value // 10
            self.rods[target_index].set_value(new_value % 10)
            target_index += 1

    def _shift_left_and_add_digit(self, digit):
        """Shift the register one decimal place and append one digit."""
        if self.rods[-1].value() != 0:
            raise ValueError("Number too large to be represented")

        for index in range(len(self.rods) - 1, 0, -1):
            self.rods[index].set_value(self.rods[index - 1].value())
        self.rods[0].set_value(digit)

    def multiply(self, number):
        """Multiply using decimal partial products and rod-level addition."""
        self._validate_operand(number)
        multiplicand_digits = [rod.value() for rod in self.rods]
        while len(multiplicand_digits) > 1 and multiplicand_digits[-1] == 0:
            multiplicand_digits.pop()

        result = Abacus(len(self.rods))
        offset = 0
        multiplier = number
        try:
            while multiplier:
                multiplier_digit = multiplier % 10
                multiplier //= 10

                # A decimal partial product is repeated addition of the
                # multiplicand, shifted to the current multiplier digit.
                for _ in range(multiplier_digit):
                    result._add_digits_at_offset(multiplicand_digits, offset)
                offset += 1
        except ValueError as error:
            raise ValueError(
                "Multiplication error: Result is too large to be represented"
            ) from error

        self._copy_value_from(result)

    def divide(self, number):
        """Divide using decimal long division and repeated subtraction."""
        self._validate_operand(number)
        if number == 0:
            raise ZeroDivisionError("Division error: Cannot divide by zero")

        quotient = Abacus(len(self.rods))
        remainder = Abacus(len(self.rods))

        for rod in reversed(self.rods):
            remainder._shift_left_and_add_digit(rod.value())

            quotient_digit = 0
            while remainder.current_value() >= number:
                remainder.subtract(number)
                quotient_digit += 1

            quotient._shift_left_and_add_digit(quotient_digit)

        if remainder.current_value() != 0:
            raise ValueError("Division error: Result is not an integer")

        self._copy_value_from(quotient)

    @staticmethod
    def _render_row(rod_displays, row, bead, empty, separator):
        return separator + separator.join(
            bead if rod_display[row] else empty
            for rod_display in rod_displays
        ) + separator

    def display(self, compact=True):
        rod_displays = [
            modify_displayed_list(rod.display())
            for rod in reversed(self.rods)
        ]

        if not compact:
            return self._display_full(rod_displays)

        display_rows = [''] * 7
        for rod_display in rod_displays:
            for i in range(7):
                display_rows[i] += ' * ' if rod_display[i] else ' | '
                display_rows[i] += ' '
        display_rows.insert(2, ' -- ' * len(self.rods))  # Separator line after binary part
        return '\n'.join(display_rows)

    def _display_full(self, rod_displays):
        cell_width = 5
        bead = '  ●  '
        empty = '  │  '
        top = '┌' + '┬'.join('─' * cell_width for _ in self.rods) + '┐'
        beam = '╞' + '╪'.join('═' * cell_width for _ in self.rods) + '╡'
        bottom = '└' + '┴'.join('─' * cell_width for _ in self.rods) + '┘'

        rows = [top]
        rows.extend(
            self._render_row(rod_displays, row, bead, empty, '│')
            for row in range(2)
        )
        rows.append(beam)
        rows.extend(
            self._render_row(rod_displays, row, bead, empty, '│')
            for row in range(2, 7)
        )
        rows.append(bottom)

        values = [rod.value() for rod in reversed(self.rods)]
        rows.append(' ' + ' '.join(f'{value:^{cell_width}}' for value in values) + ' ')
        return '\n'.join(rows)

    def reset(self):
        for rod in self.rods:
            rod.quinary = [0] * 5
            rod.binary = [0] * 2
