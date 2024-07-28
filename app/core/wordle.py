import logging
import secrets
from collections.abc import Generator
from typing import Any, Final
from uuid import UUID

from discord import Client
from discord.interactions import Interaction
from discord.ui import Select, View

from app.enums import MatchResult
from app.storage.guess import guess_repo
from app.storage.wordle import wordle_repo
from app.word_generator import Difficulty, Word, WordGenerator, get_wordgen

logger = logging.getLogger(__name__)


class UnequalInLengthError(Exception):
    """Guess and word are unequal in length."""


class WordleGameNotFoundError(Exception):
    """Exception raised when the wordle game not found."""


class WordleGame:
    """Represent a Wordle Game."""

    WORD_LENGTH_MIN: Final[int] = 5
    WORD_LENGTH_MAX: Final[int] = 15
    DEVIATED_THRESHOLD: int = 4

    def __init__(self) -> None:
        self.wordgen: WordGenerator = get_wordgen()

    def _random_length(self) -> int:
        return self.WORD_LENGTH_MIN + secrets.randbelow(
            self.WORD_LENGTH_MAX - self.WORD_LENGTH_MIN + 1,
        )

    def _gen_word(self, length: int | None, difficulty: Difficulty) -> str:
        """Generate a new word."""
        length = length or self._random_length()
        return self.wordgen.random(
            length=length, difficulty=difficulty
        ).word.upper()

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
        colors = [MatchResult.WRONG_LETTER] * length

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

    async def start(
        self,
        interaction: Interaction[Client],
        length_select: Select[View],
        difficulty_select: Select[View],
    ) -> str:
        """Start the game."""
        word = self._gen_word(
            length=int(length_select.values[0]),  # noqa:PD011
            difficulty=Difficulty(difficulty_select.values[0]),  # noqa:PD011
        )
        message = "You word is chosen."
        message += (
            f"The word has {len(word)} letters."
            if length_select.values[0] == "0"  # noqa:PD011
            else ""
        )
        message += "You can start guessing the word now."

        await wordle_repo.create(word, interaction.user.id)
        await interaction.response.send_message(content=message)
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

        if len(guess) != len(wordle.word):
            raise UnequalInLengthError

        colors = self.gen_colors_for_guess(guess=guess, word=wordle.word)
        await guess_repo.create(
            content=guess,
            result="".join(map(str, colors)),
            wordle_id=wordle.id,
        )

    async def end(self, user_id: int) -> None:
        """End the current wordle game of a user."""
        wordle = await wordle_repo.get_ongoing_wordle(
            user_id=user_id,
        )
        if not wordle:
            raise WordleGameNotFoundError
        await wordle_repo.change_status(
            id=wordle.id,
            is_winning=False,
            is_ending=True,
        )

    async def win(self, user_id: int) -> None:
        """Win the current wordle game of a user."""
        wordle = await wordle_repo.get_ongoing_wordle(
            user_id=user_id,
        )
        if not wordle:
            raise WordleGameNotFoundError
        await wordle_repo.change_status(
            id=wordle.id,
            is_winning=True,
            is_ending=False,
        )

    async def check_guess(self, user_id: int) -> bool:
        """Return True if the guess match the active wordle."""
        guesses = await wordle_repo.get_guesses(user_id=user_id)
        latest_guess = guesses[-1].result

        return not any(map(int, latest_guess))

    def check_valid_word(self, word: str) -> bool:
        """Return True if the word is valid."""
        return self.wordgen.is_valid(word.lower())

    async def wrong_guess(self, id: UUID) -> None:
        """The previous guess is wrong."""
        await wordle_repo.change_status(id=id, is_winning=False)

    async def get_hint(self, user_id: int, word: str) -> str:
        """Return hint for the user."""
        target_word: Word = self.wordgen.get_word(word=word)

        choice = secrets.randbelow(10)

        if choice < 8:  # noqa: PLR2004
            return await self.get_letter_hint(user_id=user_id)
        if choice == 8:  # noqa: PLR2004
            return f"The definition of the word is {target_word.definition}"

        return f"The synonyms of the word are {","
                .join(target_word.synonyms)}"

    async def get_letter_hint(self, user_id: int) -> str:
        """Return the correct letter at specific position."""
        wordle_game = await wordle_repo.get_ongoing_wordle(user_id=user_id)
        position = secrets.randbelow(len(wordle_game.word))

        return (
            f"{wordle_game.word[position]} is at the position {position + 1}"
        )
