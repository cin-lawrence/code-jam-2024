import unittest

import pytest
from app.core.wordle import MatchResult, UnequalInLengthError, WordleGame

GRN = MatchResult.CORRECT_LETTER_CORRECT_POSITION
YLW = MatchResult.CORRECT_LETTER_WRONG_POSITION
BLU = MatchResult.DEVIATED_LETTER_CORRECT_POSITION
PRL = MatchResult.DEVIATED_LETTER_WRONG_POSITION
RED = MatchResult.WRONG_LETTER


class TestWordleGame(unittest.TestCase):
    """Tests for WordleGame class."""

    def setUp(self) -> None:
        """Setup a game for each test."""
        self.game = WordleGame()
        self.game.DEVIATED_THRESHOLD = 4

    def test__gen_word(self) -> None:
        """Test the _gen_word() method of WordleGame.

        Checks that the letters of the generated word are upper case latin
        letters.
        """
        for length in range(
            WordleGame.WORD_LENGTH_MIN, WordleGame.WORD_LENGTH_MAX + 1
        ):
            word = self.game._gen_word(length)
            assert word.isalpha(), f"{word} is an invalid word."
            assert word.isupper(), f"{word} is not in upper case."

    def test_gen_colors_for_guess_threshold_zero(self) -> None:
        """Test the gen_colors_for_guess method of WordleGame.

        At threshold=0, no character should be marked deviated.
        """
        self.game.DEVIATED_THRESHOLD = 0
        test_cases = (
            ("A", "B", [RED]),
            ("A", "Z", [RED]),
            ("W", "W", [GRN]),
        )
        for word, guess, expected in test_cases:
            colors = list(
                self.game.gen_colors_for_guess(guess=guess, word=word)
            )
            assert expected == colors, f"expected {expected} found {colors}."

    def test_gen_colors_for_guess_threshold_one(self) -> None:
        """Test the gen_colors_for_guess method of WordleGame.

        At threshold=1, adjacent characters should be marked deviated if not
        already marked.
        """
        self.game.DEVIATED_THRESHOLD = 1
        test_cases = (
            ("A", "B", [BLU]),
            ("A", "Z", [RED]),
            ("W", "W", [GRN]),
        )
        for word, guess, expected in test_cases:
            colors = list(
                self.game.gen_colors_for_guess(guess=guess, word=word)
            )
            assert expected == colors, f"expected {expected} found {colors}."

    def test_word_length(self) -> None:
        """Incorrect word length must raise UnequalInLengthError."""
        guesses = ["ASDF", "QWERTY", ""]
        word = "HELLO"
        for guess in guesses:
            with pytest.raises(UnequalInLengthError):
                list(self.game.gen_colors_for_guess(guess=guess, word=word))

    def test_gen_colors_for_guess(self) -> None:
        """Test the gen_colors_for_guess() method of WordleGame.

        Note:
        ----
            In test case 1 (word: SPORT, guess: APPLE),
            since only one P is correct,
            second P should not be marked as "correct letter, wrong position",
            but rather as "deviated, correct position" and
            L would not be "deviated, wrong position" w.r.t. to O
            since second P was already marked as "deviated, correct position".

        """
        test_cases = (
            ("SPORT", "APPLE", [RED, GRN, BLU, RED, RED]),
            ("SPORT", "GYPSY", [RED, RED, YLW, YLW, RED]),
            ("SPORT", "SPORT", [GRN, GRN, GRN, GRN, GRN]),
            ("ABCXY", "AAAAA", [GRN, BLU, BLU, RED, RED]),
            ("AAZZZ", "MMBBB", [RED, RED, PRL, PRL, RED]),
        )
        for word, guess, expected in test_cases:
            colors = list(
                self.game.gen_colors_for_guess(guess=guess, word=word)
            )
            assert expected == colors, f"expected {expected} found {colors}."

    def test_check_valid_word(self) -> None:
        """Test the check_valid_word() method of WordleGame."""
        valid_guesses = ["hello", "HELLO", "heLLo", "PENnY"]
        invalid_guesses = ["", "hello!!", "  ", "\n", "234", "BRuhhh"]

        for guess in valid_guesses:
            assert self.game.check_valid_word(
                word=guess
            ), f"'{guess}' is a valid word."

        for guess in invalid_guesses:
            assert not self.game.check_valid_word(
                word=guess
            ), f"'{guess}' is not a valid word."


if __name__ == "__main__":
    unittest.main()
