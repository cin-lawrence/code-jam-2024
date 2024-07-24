import logging

from discord import Client, Intents, Object
from discord.ext import commands
from discord.interactions import Interaction

from .settings import BotSettings, settings

logger = logging.getLogger(__name__)

USERS = []


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
async def start_wordle(interaction: Interaction) -> None:
    """Start the wordle game."""
    if interaction.user.id in USERS:
        await interaction.response.send_message(
            "You already starts the wordle game\n\
            Please complete the current game to start a new game",
        )
    else:
        USERS.append(interaction.user.id)
        await interaction.response.send_message("Welcome to wordle")


@bot.tree.command(
    name="guess",
    description="make a guess on the wordle",
    guild=Object(id=settings.GUILD_ID),
)
async def guess(interaction: Interaction, word: str) -> None:
    """User guess the wordle."""
    if interaction.user.id in USERS:
        await interaction.response.send_message(f"Your guess is {word}")
    else:
        await interaction.response.send_message(
            "Please start the wordle game before making a guess",
        )


@bot.tree.command(
    name="end-wordle",
    description="end the current wordle game",
    guild=Object(id=settings.GUILD_ID),
)
async def end_wordle(interaction: Interaction) -> None:
    """User end the current wordle game."""
    if interaction.user.id in USERS:
        await interaction.response.send_message("The current game ends")
        USERS.remove(interaction.user.id)
    else:
        await interaction.response.send_message("You are not in a game yet")
