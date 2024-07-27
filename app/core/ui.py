from collections.abc import Sequence
from typing import Final

from discord import Embed, Interaction, Member, SelectOption, User
from discord.ui import Select, View

from app.core.wordle import WordleGame
from app.models.guess import Guess

EMOJI: Final[list[str]] = [
    ":green_heart:",
    ":yellow_heart:",
    ":blue_heart:",
    ":purple_heart:",
    ":heart:",
]


class GuessEmbed(Embed):
    """Embed that show the guesses of the player."""

    def __init__(self, user: User | Member, guesses: Sequence[Guess]) -> None:
        super().__init__(title=f"{user.name}'s Wordle Guess")

        for idx, guess in enumerate(guesses):
            self.add_field(
                name=f"Guess #{idx + 1}",
                value=(
                    f"{self._format_guess_word(guess.content)}\n{self._format_guess_result(guess.result)}"
                ),
                inline=False,
            )

    def _format_guess_word(self, word: str) -> str:
        """Format the guess word to show on the embed."""
        new_word = "  " + "     ".join(word)

        return (
            new_word.replace("L", " L ")
            .replace("J", "  J ")
            .replace("I", "  I ")
        )

    def _format_guess_result(self, word: str) -> str:
        """Format the result into emoji to show on the embed."""
        return " ".join(EMOJI[int(val)] for val in word)


class SelectionView(View):
    """View that contains all the Select."""

    def __init__(self, *, timeout: float | None = 180) -> None:
        self.length_selected = False
        self.difficulty_selected = False
        super().__init__(timeout=timeout)

        self.length_select = LengthSelect()
        self.difficulty_select = DifficultySelect()

        self.add_item(self.length_select)
        self.add_item(self.difficulty_select)

    async def start(self, interaction: Interaction) -> None:
        """Start the Wordle Game."""
        await WordleGame().start(
            interaction=interaction,
            length_select=self.length_select,
            difficulty_select=self.difficulty_select,
        )


class LengthSelect(Select):
    """Select that choose the length of a word in a Wordle Game."""

    OPTION_PLACEHOLDER: Final[str] = ""
    MIN_VALUES = 1
    MAX_VALUES = 1

    def __init__(self) -> None:
        options = [
            SelectOption(
                label=f"{val} letters",
                value=str(val),
                # description
                # emoji
            )
            for val in range(5, 16)
        ]

        super().__init__(
            placeholder=self.OPTION_PLACEHOLDER,
            min_values=self.MIN_VALUES,
            max_values=self.MAX_VALUES,
            options=options,
        )

        self.add_option(
            label="Random",
            value="0",
            description="Choose a random letter word for the Wordle Game",
        )

    async def callback(self, interaction: Interaction) -> None:
        """User made a selection."""
        self.view.length_selected = True

        if self.view.length_selected and self.view.difficulty_selected:
            await self.view.start(interaction)
        else:
            await interaction.response.defer()


class DifficultySelect(Select):
    """Select that choose the length of a word in a Wordle Game."""

    OPTION_PLACEHOLDER: Final[str] = ""
    MIN_VALUES = 1
    MAX_VALUES = 1

    def __init__(self) -> None:
        options = [
            SelectOption(
                label=val,
                value=str(idx),
                description=f"{val} Mode of Wordle",
                # emoji
            )
            for idx, val in enumerate(["Easy", "Medium", "Hard"])
        ]

        super().__init__(
            placeholder=self.OPTION_PLACEHOLDER,
            min_values=self.MIN_VALUES,
            max_values=self.MAX_VALUES,
            options=options,
        )

    async def callback(self, interaction: Interaction) -> None:
        """User made a selection."""
        self.view.difficulty_selected = True

        if self.view.length_selected and self.view.difficulty_selected:
            await self.view.start(interaction)
        else:
            await interaction.response.defer()
