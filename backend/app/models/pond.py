from typing import List

from sqlalchemy import String, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Pond(Base):
    __tablename__ = "ponds"
    __table_args__ = (UniqueConstraint("hatchery_id", "pond_code", name="uq_hatchery_pond_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    hatchery_id: Mapped[int] = mapped_column(ForeignKey("hatcheries.id"), nullable=False, index=True)
    pond_code: Mapped[str] = mapped_column(String(64), nullable=False)
    species: Mapped[str] = mapped_column(String(64), nullable=False)
    volume_m3: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="stocked")

    hatchery: Mapped["Hatchery"] = relationship("Hatchery", back_populates="ponds")
    water_samples: Mapped[List["WaterSample"]] = relationship(
        "WaterSample", back_populates="pond", cascade="all, delete-orphan"
    )
    feed_events: Mapped[List["FeedEvent"]] = relationship(
        "FeedEvent", back_populates="pond", cascade="all, delete-orphan"
    )
