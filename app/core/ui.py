from typing import Final

from discord import Embed, Member, SelectMenu, User
from models.wordle import Guess, Wordle

EMOJI: Final[list[str]] = [
    ":green_heart:",
    ":yellow_heart:",
    ":blue_heart:",
    ":purple_heart:",
    ":heart:",
]


def form_embed(user: User | Member, wordle: Wordle) -> Embed:
    """Form the embed to show the user their guess' details."""
    embed = Embed(title=f"{user.name}'s Wordle Guess")

    guesses: list[Guess] = wordle.guesses

    for idx, guess in enumerate(guesses):
        embed.add_field(
            name=f"Guess #{idx + 1}",
            value=guess,
        )

    return embed


def form_select_menu() -> SelectMenu:
    """Form the SelectMenu for the user to choose length of word."""


def _format_guess_word(word: str) -> str:
    """Format the guess word to show on the embed."""
    return word


def _format_guess_result(word: str) -> str:
    """Format the result into emoji to show on the embed."""
    return word
