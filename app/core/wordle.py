import asyncio
import secrets
from collections.abc import Generator
from enum import IntEnum
from typing import Any, Final

from app.storage.guess import guess_repo
from app.storage.wordle import wordle_repo
from app.word_generator import WordGenerator


class UnequalInLengthError(Exception):
    """Guess and word are unequal in length."""


class WordleGameNotFoundError(Exception):
    """Exception raised when the wordle game not found."""


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

    def __init__(self) -> None:
        self.wordgen = WordGenerator()

    def _random_length(self) -> int:
        return self.WORD_LENGTH_MIN + secrets.randbelow(
            self.WORD_LENGTH_MAX - self.WORD_LENGTH_MIN + 1,
        )

    def _gen_word(self, length: int | None = None) -> str:
        """Generate a new word."""
        length = length or self._random_length()
        return self.wordgen.random(length=length).word

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
            abs(guess_ascii - ord(ch)) < self.DEVIATED_THRESHOLD for ch in word
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
            print(f"guess {len(guess)}")
            print(f"word {len(word)}")
            raise UnequalInLengthError
        for guesschar, wordchar in zip(guess, word, strict=False):
            yield self._gen_color(guesschar, wordchar, word)

    async def start(self, user_id: int, length: int | None = None) -> str:
        """Start the game."""
        word = self._gen_word(length=length)
        await wordle_repo.create(word, user_id)
        return word

    async def guess(
        self,
        user_id: int,
        guess: str,
    ) -> None:
        """Save the guess result into the DB."""
        wordle = await wordle_repo.get_active_wordle_by_user_id(
            user_id=user_id,
        )
        if wordle is None:
            raise ValueError("wordle game not found for user %d" % user_id)

        colors = self.gen_colors_for_guess(guess=guess, word=wordle.word)
        await guess_repo.create(
            content=guess,
            result="".join(map(str, colors)),
            wordle_id=wordle.id,
        )

    async def end(self, user_id: int) -> None:
        """End the current wordle game of a user."""
        wordle = await wordle_repo.get_active_wordle_by_user_id(
            user_id=user_id,
        )
        if not wordle:
            raise WordleGameNotFoundError
        await wordle_repo.change_status(wordle.id)

    async def check_guess(self, user_id: int) -> bool:
        """Return True if the guess match the active wordle."""
        guesses = await wordle_repo.get_guesses(user_id=user_id)
        latest_guess = guesses[-1].result

        return not any(map(int, latest_guess))

    def check_valid_word(self, word: str) -> bool:
        """Return True if the word is valid."""
        return self.wordgen.is_valid(word)


if __name__ == "__main__":
    import asyncio

    from app.models.base import Base
    from app.storage.database import database

    async def main() -> None:
        """Main function."""
        async with database.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        game = WordleGame()
        await game.start(1234, 5)

    asyncio.run(main())
