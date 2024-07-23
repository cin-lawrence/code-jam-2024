import asyncio
import random
from collections.abc import Generator
from typing import Any

from ..storage.wordle import wordle_repo
from ..storage.guess import guess_repo


def get_word(length: int | None = None) -> str:
    """Get a word with specified length."""
    if length is None:
        length = random.randint(5, 15)

    word = "foobar"

    return word


def color_for_guess(
    guess: str | tuple[str] | list[str],
    word: str | tuple[str] | list[str],
) -> Generator[int, Any, Any]:
    """Get the integer representing the status."""
    if len(guess) > len(word) or len(guess) < len(word):
        pass  # TODO
    else:
        for g_letter, w_letter in zip(guess, word, strict=False):
            yield _get_color_code(g_letter, w_letter, word)


def _get_color_code(guess_letter: str, word_letter: str, word: str) -> int:
    """- ❤️  for wrong letter (4)
    - 💛  for correct letter, wrong position (1)
    - 💚  for correct letter, correct location (0)
    - 💙  for deviated letter, correct position (2)
    - 💜  for deviated letter, wrong position (3)
    """
    # A = 65
    # Z = 90
    guess_ascii = ord(guess_letter)
    word_ascii = ord(word_letter)

    if guess_letter == word_letter:
        return 0

    if guess_letter in word:
        return 1

    if abs(guess_ascii - word_ascii) < 4:
        return 2

    if any(map(lambda x: abs(guess_ascii - ord(x)) < 4, word)):
        return 3

    return 4


def start_wordle(user_id: str, length: int | None = None) -> str:
    """Start the wordle game by creating a new word and store in db."""
    word = get_word(length)
    asyncio.run(wordle_repo.create(word, user_id))

    return word


def guess_wordle(user_id: str, guess_word: str) -> Generator[int, Any, Any]:
    """Check if the wordle is correct and store the guess in db."""
    word = asyncio.run(wordle_repo.get_by_user_id(user_id)).word

    colors = color_for_guess(guess_word, word)

    # TODO : save guess into the db

    return colors


# quick test
"""
if __name__ == "__main__":
    import asyncio

    from app.models.base import Base
    from app.storage.database import database

    async def main():
        async with database.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(main())

    start_wordle("1234", 8)
    print(list(guess_wordle("1234", "laalaa")))
"""
