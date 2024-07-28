from app.models.player import Player

from .database import Database, database


class PlayerRepo:
    """Repository for players."""

    def __init__(self, db: Database) -> None:
        self.db: Database = db

    async def create(
        self,
        userid: int,
        username: str,
        display_name: str,
    ) -> Player:
        """Create a new player from discord user."""
        async with self.db.create_session() as session:
            player = Player(
                id=userid,
                username=username,
                display_name=display_name,
            )
            session.add(player)
            await session.commit()
            await session.refresh(player)
            return player


player_repo = PlayerRepo(database)
