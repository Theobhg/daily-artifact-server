"""Modelo de Artifact: o registro unico de cada dia."""

from __future__ import annotations

import enum
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.tag import Tag, artifact_tags


class ArtifactType(str, enum.Enum):
    """Formatos aceitos para representar um dia."""

    TEXT = "text"
    QUOTE = "quote"
    PHOTO = "photo"
    LINK = "link"
    MUSIC = "music"


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Artifact(Base):
    """Artefato que representa um unico dia.

    A unicidade de artifact_date e garantida por constraint no banco, alem da
    validacao feita pelo ArtifactService antes de gravar.
    """

    __tablename__ = "artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    artifact_date: Mapped[date] = mapped_column(Date, unique=True, index=True, nullable=False)
    type: Mapped[ArtifactType] = mapped_column(
        Enum(ArtifactType, values_callable=lambda enum_cls: [item.value for item in enum_cls]),
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(String(120), nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_now, onupdate=_now, nullable=False
    )

    # selectin evita o problema de N+1 ao listar artefatos com suas tags.
    tags: Mapped[list[Tag]] = relationship(
        secondary=artifact_tags,
        back_populates="artifacts",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Artifact {self.artifact_date} ({self.type.value})>"
