from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, desc
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


if TYPE_CHECKING:
    from .guess import Guess


class Wordle(Base):
    __tablename__ = 'guesses'

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    word: Mapped[str]
    user_id: Mapped[int]

    guesses: Mapped[list['Guess']] = relationship(
        back_populates='wordle',
        order_by=desc('Guess.created_at'),
    )
