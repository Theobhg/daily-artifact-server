"""Acesso ao banco para a entidade Artifact."""

from datetime import date

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.models.artifact import Artifact, ArtifactType
from app.models.tag import Tag


class ArtifactRepository:
    """Consultas e gravacoes de artefatos.

    Nao contem regra de negocio: apenas traduz intencoes em SQL.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, artifact: Artifact) -> Artifact:
        """Grava um novo artefato."""
        self._db.add(artifact)
        self._db.commit()
        self._db.refresh(artifact)
        return artifact

    def get_by_id(self, artifact_id: int) -> Artifact | None:
        """Busca um artefato pelo identificador."""
        return self._db.get(Artifact, artifact_id)

    def get_by_date(self, artifact_date: date) -> Artifact | None:
        """Busca o artefato registrado em uma data."""
        return self._db.scalar(select(Artifact).where(Artifact.artifact_date == artifact_date))

    def list(
        self,
        *,
        type: ArtifactType | None = None,
        year: int | None = None,
        month: int | None = None,
        tag: str | None = None,
    ) -> list[Artifact]:
        """Lista artefatos do mais recente para o mais antigo, aplicando filtros."""
        query = select(Artifact)

        if type is not None:
            query = query.where(Artifact.type == type)
        if year is not None:
            query = query.where(extract("year", Artifact.artifact_date) == year)
        if month is not None:
            query = query.where(extract("month", Artifact.artifact_date) == month)
        if tag is not None:
            query = query.join(Artifact.tags).where(Tag.name == tag)

        query = query.order_by(Artifact.artifact_date.desc())
        return list(self._db.scalars(query).unique().all())

    def get_random(self) -> Artifact | None:
        """Sorteia um artefato qualquer da colecao."""
        return self._db.scalar(select(Artifact).order_by(func.random()).limit(1))

    def update(self, artifact: Artifact) -> Artifact:
        """Persiste as alteracoes feitas em um artefato ja carregado."""
        self._db.commit()
        self._db.refresh(artifact)
        return artifact

    def delete(self, artifact: Artifact) -> None:
        """Remove um artefato."""
        self._db.delete(artifact)
        self._db.commit()
