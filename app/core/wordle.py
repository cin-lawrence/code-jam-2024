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
        return self.wordgen.random(length=length).word.upper()

    def gen_colors_for_guess(  # noqa: C901, PLR0912
        self,
        guess: str,
        word: str,
    ) -> Generator[int, Any, Any]:
        """Generate the guess result in integers.

        - ❤️  for wrong letter (4)
        - 💛  for correct letter, wrong position (1)
        - 💚  for correct letter, correct location (0)
        - 💙  for deviated letter, correct position (2)
        - 💜  for deviated letter, wrong position (3)
        """
        length = len(guess)
        if length != len(word):
            raise UnequalInLengthError

        word_used = [False] * length
        guess_used = [False] * length
        colors = [False] * length

        # Correct Letter, Correct Position
        for i in range(length):
            if guess[i] == word[i]:
                word_used[i] = True
                guess_used[i] = True
                colors[i] = MatchResult.CORRECT_LETTER_CORRECT_POSITION

        # Correct Letter, Wrong Position
        for i in range(length):
            if guess_used[i]:
                continue
            for j in range(length):
                if not word_used[j] and guess[i] == word[j]:
                    word_used[j] = True
                    guess_used[i] = True
                    colors[i] = MatchResult.CORRECT_LETTER_WRONG_POSITION
                    break

        # Deviated Letter, Correct Position
        for i in range(length):
            if guess_used[i] or word_used[i]:
                continue
            if abs(ord(guess[i]) - ord(word[i])) <= self.DEVIATED_THRESHOLD:
                word_used[i] = True
                guess_used[i] = True
                colors[i] = MatchResult.DEVIATED_LETTER_CORRECT_POSITION

        # Deviated Letter, Wrong Position
        for i in range(length):
            if guess_used[i]:
                continue
            for j in range(length):
                if (
                    not word_used[j]
                    and abs(ord(guess[i]) - ord(word[j]))
                    <= self.DEVIATED_THRESHOLD
                ):
                    word_used[j] = True
                    guess_used[i] = True
                    colors[i] = MatchResult.DEVIATED_LETTER_WRONG_POSITION
                    break
            else:
                colors[i] = MatchResult.WRONG_LETTER

        yield from colors

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
        return self.wordgen.is_valid(word.lower())


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
