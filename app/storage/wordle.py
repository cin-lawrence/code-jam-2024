from uuid import UUID

from sqlalchemy import select

from app.models.wordle import Wordle

from .database import Database, database


class WordleRepo:
    """Repository for interacting with Wordle."""

    def __init__(self, db: Database) -> None:
        self.db: Database = db

    async def create(
        self,
        word: str,
        user_id: int,
    ) -> Wordle:
        """Create a wordle."""
        async with self.db.create_session() as session:
            wordle = Wordle(word=word, user_id=user_id)
            session.add(wordle)
            await session.commit()
            await session.refresh(wordle)
            return wordle

    async def get(self, id: UUID) -> Wordle | None:
        """Get wordle by id."""
        async with self.db.create_session() as session:
            stmt = select(Wordle).where(Wordle.id == id)
            result = await session.execute(stmt)
            wordle: Wordle | None = result.scalar()
            return wordle

    async def get_by_user_id(self, user_id: str) -> Wordle | None:
        """Get wordle by user id."""
        async with self.db.create_session() as session:
            stmt = select(Wordle).where(Wordle.user_id == user_id)
            result = await session.execute(stmt)
            wordle: Wordle | None = result.scalar()
            return wordle


# TODO: move this to a container
wordle_repo = WordleRepo(database)
