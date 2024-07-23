from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .wordle import Wordle


class Guess(Base):
    __tablename__ = 'guesses'

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    content: Mapped[str]
    result: Mapped[str]
    wordle_id: Mapped[UUID] = mapped_column(ForeignKey('wordle.id'))

    wordle: Mapped[Wordle] = relationship(back_populates='guesses')
