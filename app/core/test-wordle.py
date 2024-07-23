import unittest
from collections.abc import Generator

from wordle import color_for_guess


class TestWordle(unittest.TestCase):
    def test_color_for_guess(self):
        guess = "zehfq"
        word = "hello"
        colors = color_for_guess(guess, word)
        self.assertIsInstance(colors, Generator)
        self.assertEqual([4, 0, 1, 3, 2], list(colors))


unittest.main()
