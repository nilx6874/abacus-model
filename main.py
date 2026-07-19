#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abacus import abacus_models


def show_abacus(abacus, title):
    print(title)
    print(abacus.display(compact=False))
    print(f"Value: {abacus.current_value()}\n")


def main():
    # Example usage with a full console representation after each calculation.
    abacus = abacus_models.Abacus(rods=10)
    show_abacus(abacus, "Initial state")

    abacus.add(300)
    show_abacus(abacus, "After adding 3")

    abacus.add(99)
    show_abacus(abacus, "After adding 12")

    abacus.subtract(6)
    show_abacus(abacus, "After subtracting 6")


if __name__ == "__main__":
    main()
