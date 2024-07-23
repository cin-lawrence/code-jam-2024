from uuid import UUID

from ..models.guess import Guess
from .database import Database, database

from sqlalchemy import select


class GuessRepo:
    def __init__(self, db: Database) -> None:
        self.db: Database = db

    async def create(
        self,
        content: str,
        result: str,
        wordle_id: UUID,
    ) -> Guess:
        async with self.db.create_session() as session:
            guess = Guess(content=content, result=result, wordle_id=wordle_id)
            session.add(guess)
            await session.commit()
            await session.refresh(guess)
            return guess

    async def get_guess(self, id: UUID) -> Guess | None:
        async with self.db.create_session() as session:
            stmt = select(Guess).where(Guess.id == id)
            result = await session.execute(stmt)
            guess: Guess | None = result.scalar()
            return guess


# TODO: move this to a container
guess_repo = GuessRepo(database)
