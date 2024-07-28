import logging
from typing import cast

from discord import Client, Intents, Object
from discord.channel import TextChannel
from discord.ext import commands
from discord.interactions import Interaction

from .core import ui
from .core.wordle import WordleGame
from .settings import BotSettings, settings
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
    logger.log(
        0,
        await wordle_repo.get_active_wordle_by_user_id(interaction.user.id),
    )
    if await wordle_repo.get_active_wordle_by_user_id(interaction.user.id):
        await interaction.response.send_message(
            "You already starts the wordle game\n\
            Please complete the current game to start a new game",
        )
    else:
        await WordleGame().start(user_id=interaction.user.id, length=5)
        await interaction.response.send_message("Welcome to wordle")


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

    if await wordle_repo.get_active_wordle_by_user_id(
        user_id=interaction.user.id,
    ):
        await wordle.guess(
            user_id=interaction.user.id,
            guess=word.upper(),
        )

        embed = ui.form_embed(
            user=interaction.user,
            guesses=await wordle_repo.get_guesses(user_id=interaction.user.id),
        )

        await interaction.response.send_message(embed=embed)

    else:
        await interaction.response.send_message(
            "Please start the wordle game before making a guess",
        )
        return

    results = await wordle_repo.get_guesses(interaction.user.id)
    if await wordle.check_guess(interaction.user.id):
        await wordle.end(interaction.user.id)

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
    ):
        await interaction.response.send_message("The current game ends")

        await WordleGame().end(interaction.user.id)

    else:
        await interaction.response.send_message("You are not in a game yet.")
