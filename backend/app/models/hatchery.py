from typing import Optional, List

from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Hatchery(Base):
    __tablename__ = "hatcheries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    seawater_source: Mapped[str] = mapped_column(String(128), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    ponds: Mapped[List["Pond"]] = relationship(
        "Pond", back_populates="hatchery", cascade="all, delete-orphan"
    )
