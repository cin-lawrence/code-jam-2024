import logging
from typing import cast
from uuid import UUID

from discord import Client, Intents, Object, TextChannel
from discord.ext import commands
from discord.interactions import Interaction

from .core import ui
from .core.wordle import UnequalInLengthError, WordleGame
from .models.wordle import Wordle, WordleStatus
from .settings import BotSettings, settings
from .storage.player import player_repo
from .storage.trivia import trivia_repo
from .storage.wordle import wordle_repo

logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    """Overriden class for the default discord Bot."""

    def __init__(self, settings: BotSettings) -> None:
        self.settings = settings
        super().__init__(settings.COMMAND_PREFIX, intents=Intents.default())

    async def on_ready(self) -> None:
        """Overriden method on_ready."""
        logger.warning(
            "[bot] syncing commands into server %s",
            self.settings.GUILD_ID,
        )
        await bot.tree.sync(guild=Object(id=settings.GUILD_ID))
        logger.warning("DONE syncing commands!")


bot = Bot(settings)


@bot.tree.command(
    name="jam",
    description="CodeJam Hello World!",
    guild=Object(id=settings.GUILD_ID),
)
async def hello_world(interaction: Interaction[Client]) -> None:
    """Says hello world."""
    await interaction.response.send_message("Hello World!")


@bot.tree.command(
    name="start-wordle",
    description="Start the wordle game",
    guild=Object(id=settings.GUILD_ID),
)
async def start_wordle(interaction: Interaction[Client]) -> None:
    """Start the wordle game."""
    if await wordle_repo.get_active_wordle_by_user_id(interaction.user.id):
        await interaction.response.send_message(
            "You already starts the wordle game\n\
            Please complete the current game to start a new game",
        )
        return

    player = await player_repo.get(interaction.user.id)
    if player is None:
        await player_repo.create(
            userid=interaction.user.id,
            username=interaction.user.name,
            display_name=interaction.user.display_name,
        )
    await interaction.response.defer()

    view_menu = ui.StartSelectionView()

    await interaction.followup.send("Welcome to wordle", view=view_menu)


@bot.tree.command(
    name="guess",
    description="make a guess on the wordle",
    guild=Object(id=settings.GUILD_ID),
)
async def guess(interaction: Interaction[Client], word: str) -> None:
    """User guess the wordle."""
    wordle = WordleGame()

    if not wordle.check_valid_word(word=word.upper()):
        await interaction.response.send_message(
            f"{word.upper()} is not a valid word.",
        )
        return

    wordle: Wordle | None = await wordle_repo.get_ongoing_wordle(
        interaction.user.id,
    )
    if wordle is None:
        message = "Please start the wordle game before making a guess."
        await interaction.response.send_message(message)
        return

    match wordle.status:
        case WordleStatus.ACTIVE:
            try:
                await wordle.guess(
                    user_id=interaction.user.id,
                    guess=word.upper(),
                )
            except UnequalInLengthError:
                message = "The length of guess and the word are not the same"
                await interaction.response.send_message(content=message)
                return
            else:
                embed = ui.GuessEmbed(
                    user=interaction.user,
                    guesses=await wordle_repo.get_guesses(
                        user_id=interaction.user.id
                    ),
                )

                await interaction.response.send_message(embed=embed)
        case WordleStatus.PENDING:
            message = (
                "Please complete the trivia question first "
                "before continue guessing"
            )
            await interaction.response.send_message(message)
            return
        case _:
            return

    if not (await wordle.check_guess(interaction.user.id)):
        await wordle.wrong_guess(id=wordle.id)
        wordle = await wordle_repo.get_pending_wordle(interaction.user.id)

        if wordle:
            await trivial(interaction=interaction, wordle_id=wordle.id)
            return

    await wordle.end(interaction.user.id)
    results = await wordle_repo.get_guesses(interaction.user.id)
    await cast(TextChannel, interaction.channel).send(
        content=f"Congratulations! {interaction.user.name} \
            has guess the correct word in {len(results)} guess(es)",
    )


@bot.tree.command(
    name="end-wordle",
    description="end the current wordle game",
    guild=Object(id=settings.GUILD_ID),
)
async def end_wordle(interaction: Interaction[Client]) -> None:
    """User end the current wordle game."""
    if await wordle_repo.get_active_wordle_by_user_id(
        user_id=interaction.user.id,
    ) or await wordle_repo.get_pending_wordle(user_id=interaction.user.id):
        await interaction.response.send_message("The current game ends")

        await WordleGame().end(interaction.user.id)

    else:
        await interaction.response.send_message("You are not in a game yet.")


async def trivial(interaction: Interaction[Client], wordle_id: UUID) -> None:
    """Show the trivial question."""
    trivia_ques = await trivia_repo.get_random()

    view = ui.TrivialSelectionView(
        correct_answer=trivia_ques.correct_answer,
        wrong_answers=[
            trivia_ques.incorrect_answer_1,
            trivia_ques.incorrect_answer_2,
            trivia_ques.incorrect_answer_3,
        ],
        wordle_id=wordle_id,
    )

    if interaction.response.is_done():
        await interaction.followup.send(
            content=trivia_ques.question, view=view
        )
    else:
        await interaction.response.send_message(
            content=trivia_ques.question, view=view
        )
