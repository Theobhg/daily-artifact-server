"""Modelo de Tag e tabela associativa com Artifact."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.artifact import Artifact

# Tabela associativa do relacionamento N:N entre Artifact e Tag.
artifact_tags = Table(
    "artifact_tags",
    Base.metadata,
    Column("artifact_id", Integer, ForeignKey("artifacts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    """Rotulo reaproveitavel entre artefatos.

    O nome e sempre persistido normalizado em minusculas, o que torna o
    controle de duplicidade naturalmente case-insensitive.
    """

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    artifacts: Mapped[list["Artifact"]] = relationship(
        secondary=artifact_tags,
        back_populates="tags",
    )

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"
