import asyncio
import secrets
from collections.abc import Generator
from enum import IntEnum
from typing import Any, Final

from app.storage.wordle import wordle_repo


class UnequalInLengthError(Exception):
    """Guess and word are unequal in length."""


class MatchResult(IntEnum):
    """Meaningful guess result."""

    CORRECT_LETTER_CORRECT_POSITION = 0
    CORRECT_LETTER_WRONG_POSITION = 1
    DEVIATED_LETTER_CORRECT_POSITION = 2
    DEVIATED_LETTER_WRONG_POSITION = 3
    WRONG_LETTER = 4


class WordleGame:
    """Represent a Wordle Game."""

    WORD_LENGTH_MIN: Final[int] = 5
    WORD_LENGTH_MAX: Final[int] = 15
    DEVIATED_THRESHOLD: Final[int] = 4

    def _random_length(self) -> int:
        return self.WORD_LENGTH_MIN + secrets.randbelow(
            self.WORD_LENGTH_MAX - self.WORD_LENGTH_MIN + 1,
        )

    def gen_word(self, length: int | None = None) -> str:
        """Generate a new word."""
        length = length or self._random_length()
        # TODO: remove the hardcoded word
        word: str = "foobar"
        return word

    def _gen_color(
        self,
        guesschar: str,
        wordchar: str,
        word: str,
    ) -> int:
        """Generate color for each char.

        - ❤️  for wrong letter (4)
        - 💛  for correct letter, wrong position (1)
        - 💚  for correct letter, correct location (0)
        - 💙  for deviated letter, correct position (2)
        - 💜  for deviated letter, wrong position (3)
        """
        if guesschar == wordchar:
            return MatchResult.CORRECT_LETTER_CORRECT_POSITION
        if guesschar in word:
            return MatchResult.CORRECT_LETTER_WRONG_POSITION
        guess_ascii: int = ord(guesschar)
        word_ascii: int = ord(wordchar)
        if abs(guess_ascii - word_ascii) < self.DEVIATED_THRESHOLD:
            return MatchResult.DEVIATED_LETTER_CORRECT_POSITION
        if any(
            lambda ch: abs(guess_ascii - ord(ch)) < self.DEVIATED_THRESHOLD,
            word,
        ):
            return MatchResult.DEVIATED_LETTER_WRONG_POSITION
        return MatchResult.WRONG_LETTER

    def gen_colors_for_guess(
        self,
        guess: str,
        word: str,
    ) -> Generator[int, Any, Any]:
        """Generate the guess result in integers."""
        if len(guess) != len(word):
            raise UnequalInLengthError
        for guesschar, wordchar in zip(guess, word, strict=False):
            yield self._gen_color(guesschar, wordchar, word)

    async def start(self, user_id: int, length: int | None = None) -> str:
        """Start the game."""
        word = self.gen_word(length=length)
        await wordle_repo.create(word, user_id)
        return word

    async def guess(
        self,
        user_id: int,
        guess: str,
    ) -> Generator[int, Any, Any]:
        """Return the guess result."""
        wordle = await wordle_repo.get_by_user_id(user_id)
        if wordle is None:
            raise ValueError("wordle game not found for user %d" % user_id)
        # TODO: save guess into db
        return self.gen_colors_for_guess(guess, wordle.word)


if __name__ == "__main__":
    import asyncio

    from app.models.base import Base
    from app.storage.database import database

    async def main() -> None:
        """Main function."""
        async with database.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        game = WordleGame()
        await game.start(1234, 8)
        await game.guess(1234, "laalaa")

    asyncio.run(main())
