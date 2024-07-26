import logging
import asyncio
from discord import Client, Intents, Object
from discord.ext import commands
from discord.interactions import Interaction

from .math_questions import generate_math_problem
from .trivia_questions import get_trivia
from .settings import BotSettings, settings

logger = logging.getLogger(__name__)

class Bot(commands.Bot):
    """Overridden class for the default discord Bot."""

    def __init__(self, settings: BotSettings) -> None:
        self.settings = settings
        super().__init__(settings.COMMAND_PREFIX, intents=Intents.default())

    async def on_ready(self) -> None:
        """Overridden method on_ready."""
        logger.warning(
            "[bot] syncing commands into server %s",
            self.settings.GUILD_ID,
        )
        await bot.tree.sync(guild=Object(id=settings.GUILD_ID))
        logger.warning("DONE syncing commands!")

bot = Bot(settings)

@bot.tree.command(
    name="alex",
    description="CodeJam Hello World!",
    guild=Object(id=settings.GUILD_ID),
)
async def hello_world(interaction: Interaction[Client]) -> None:
    """Says hello world."""
    await interaction.response.send_message("Hello World!")

@bot.tree.command(
    name="math",
    description="CodeJam Hello World!",
    guild=Object(id=settings.GUILD_ID),
)
async def quest_ans(interaction: Interaction[Client]) -> None:
    """math question"""
    quest, ans = generate_math_problem()
    await interaction.response.send_message(quest)

    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)  # Wait for the user's response
    except asyncio.TimeoutError:
        await interaction.followup.send("You took too long to respond!")
        return

    user_answer = msg.content.strip()
    correct_answer = ans.strip()

    if user_answer == correct_answer:
        await interaction.followup.send("Correct! 🎉")
    else:
        await interaction.followup.send(f"Incorrect. The correct answer was: {correct_answer}")

@bot.tree.command(
    name="trivia",
    description="CodeJam Hello World!",
    guild=Object(id=settings.GUILD_ID),
)
async def trivia_q(interaction: Interaction[Client]) -> None:
    """trivia."""
    quest = get_trivia()
    await interaction.response.send_message(quest)