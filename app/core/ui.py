from typing import Final

from discord import Embed, Member, SelectMenu, User

from app.models.guess import Guess

EMOJI: Final[list[str]] = [
    ":green_heart:",
    ":yellow_heart:",
    ":blue_heart:",
    ":purple_heart:",
    ":heart:",
]


def form_embed(user: User | Member, guesses: list[Guess]) -> Embed:
    """Form the embed to show the user their guess' details."""
    embed = Embed(title=f"{user.name}'s Wordle Guess")

    for idx, guess in enumerate(guesses):
        embed.add_field(
            name=f"Guess #{idx + 1}",
            value=(
                f"{_format_guess_word(guess.content)}\n{_format_guess_result(guess.result)}"
            ),
            inline=False,
        )

    return embed


def form_select_menu() -> SelectMenu:
    """Form the SelectMenu for the user to choose length of word."""


def _format_guess_word(word: str) -> str:
    """Format the guess word to show on the embed."""
    new_word = "  " + "     ".join(word)

    return (
        new_word.replace("L", " L ").replace("J", "  J ").replace("I", "  I ")
    )


def _format_guess_result(word: str) -> str:
    """Format the result into emoji to show on the embed."""
    return " ".join(EMOJI[int(val)] for val in word)
