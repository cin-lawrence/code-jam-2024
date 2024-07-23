import asyncio
import logging

from .bot import bot
from .models.base import Base
from .models.guess import Guess  # noqa: F401
from .models.wordle import Wordle  # noqa: F401
from .settings import settings
from .storage.database import database


async def init_db() -> None:
    async with database.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def main() -> None:
    """Run the app."""
    logging.basicConfig(level=logging.INFO)
    # TODO: move this to bot start hook
    asyncio.run(init_db())
    bot.run(settings.DISCORD_TOKEN)


if __name__ == "__main__":
    main()
