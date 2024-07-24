import asyncio
import logging

from discord import Client, Intents, Object
from discord.ext import commands
from discord.interactions import Interaction

from .ai_output import llama_sum
from .settings import BotSettings, settings
from .word_generator import WordGenerator

logger = logging.getLogger(__name__)

generate = WordGenerator()


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
    name="generate",
    description="Generate Word",
    guild=Object(id=settings.GUILD_ID),
)
async def gen(interaction: Interaction[Client]) -> None:
    """Generate"""
    word = generate.random()
    await interaction.response.send_message("Generating response...")
    # Get the Future object from llama_sum
    future = llama_sum(
        f"Say something about {word.word} in less than 100 words",
    )

    # Get the event loop
    loop = asyncio.get_event_loop()

    # Wait for the Future to complete and get the result
    response = await loop.run_in_executor(None, future.result)

    # Extract the 'response' key from the result
    ll = response["response"]

    # Then edit the response later with the actual message
    await interaction.edit_original_response(
        content=f"Random word is {word.word} ai says this about the word {ll}",
    )
