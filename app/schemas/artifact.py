"""Schemas Pydantic de entrada e saida da API."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.artifact import ArtifactType

# Tipos cujo conteudo textual e a propria memoria registrada.
TEXTUAL_TYPES = {ArtifactType.TEXT, ArtifactType.QUOTE}

# Tipos que apontam para um recurso externo.
LINKED_TYPES = {ArtifactType.PHOTO, ArtifactType.LINK, ArtifactType.MUSIC}


class ArtifactBase(BaseModel):
    """Campos comuns a criacao e atualizacao de um artefato."""

    artifact_date: date = Field(
        description="Dia representado pelo artefato, no formato ISO (YYYY-MM-DD).",
    )
    type: ArtifactType = Field(
        description="Formato do artefato: text, quote, photo, link ou music.",
    )
    title: str | None = Field(
        default=None,
        max_length=120,
        description="Titulo opcional do artefato.",
    )
    content: str | None = Field(
        default=None,
        description=(
            "Conteudo do artefato. Obrigatorio para os tipos text e quote; "
            "nos demais funciona como legenda ou comentario."
        ),
    )
    url: str | None = Field(
        default=None,
        max_length=2048,
        description="Endereco do recurso. Obrigatorio para photo, link e music.",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Lista de tags. Sao normalizadas em minusculas e reaproveitadas.",
    )

    @field_validator("title", "content", "url", mode="before")
    @classmethod
    def blank_to_none(cls, value: Any) -> Any:
        """Trata strings vazias ou so com espacos como ausencia de valor."""
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value

    @model_validator(mode="after")
    def check_required_field_for_type(self) -> "ArtifactBase":
        """Aplica a exigencia de campo que varia conforme o tipo do artefato."""
        if self.type in TEXTUAL_TYPES and not self.content:
            raise ValueError(f"content e obrigatorio para artefatos do tipo '{self.type.value}'")
        if self.type in LINKED_TYPES and not self.url:
            raise ValueError(f"url e obrigatoria para artefatos do tipo '{self.type.value}'")
        return self


_CREATE_EXAMPLE = {
    "artifact_date": "2026-09-20",
    "type": "quote",
    "title": "Anotado no fim da tarde",
    "content": "O dia inteiro cabe em uma frase, se a frase for a certa.",
    "url": None,
    "tags": ["memoria", "leitura"],
}


class ArtifactCreate(ArtifactBase):
    """Dados necessarios para registrar um novo artefato."""

    model_config = ConfigDict(json_schema_extra={"example": _CREATE_EXAMPLE})


class ArtifactUpdate(ArtifactBase):
    """Dados de substituicao completa de um artefato existente (PUT)."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                **_CREATE_EXAMPLE,
                "title": "Anotado no fim da tarde (revisado)",
                "tags": ["memoria"],
            }
        }
    )


class ArtifactResponse(BaseModel):
    """Representacao de um artefato retornada pela API."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                **_CREATE_EXAMPLE,
                "id": 1,
                "created_at": "2026-09-20T18:32:10",
                "updated_at": "2026-09-20T18:32:10",
            }
        },
    )

    id: int
    artifact_date: date
    type: ArtifactType
    title: str | None
    content: str | None
    url: str | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    @field_validator("tags", mode="before")
    @classmethod
    def tags_as_names(cls, value: Any) -> Any:
        """Converte os objetos Tag do ORM na lista de strings exposta pela API."""
        if isinstance(value, (list, tuple, set)):
            return [item if isinstance(item, str) else item.name for item in value]
        return value
