"""Regras de negocio dos artefatos diarios."""

from datetime import date

from sqlalchemy.orm import Session

from app.exceptions import (
    ArtifactNotFoundError,
    DuplicateDateError,
    EmptyCollectionError,
    FutureDateError,
)
from app.models.artifact import Artifact, ArtifactType
from app.repositories.artifact_repository import ArtifactRepository
from app.repositories.tag_repository import TagRepository
from app.schemas.artifact import ArtifactCreate, ArtifactUpdate

MAX_TAGS = 10


class ArtifactService:
    """Coordena as regras do dominio e os repositorios.

    Responsabilidades: impedir datas futuras, garantir um unico artefato por
    dia, normalizar tags e orquestrar a persistencia. As validacoes de formato
    e as exigencias por tipo ficam nos schemas Pydantic.
    """

    def __init__(self, db: Session) -> None:
        self._artifacts = ArtifactRepository(db)
        self._tags = TagRepository(db)

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def list_artifacts(
        self,
        *,
        type: ArtifactType | None = None,
        year: int | None = None,
        month: int | None = None,
        tag: str | None = None,
    ) -> list[Artifact]:
        """Lista artefatos do mais recente para o mais antigo."""
        return self._artifacts.list(
            type=type,
            year=year,
            month=month,
            tag=self._normalize_tag(tag),
        )

    def get_artifact(self, artifact_id: int) -> Artifact:
        """Busca um artefato por id ou falha com 404."""
        artifact = self._artifacts.get_by_id(artifact_id)
        if artifact is None:
            raise ArtifactNotFoundError(f"Nenhum artefato encontrado com o id {artifact_id}.")
        return artifact

    def get_artifact_by_date(self, artifact_date: date) -> Artifact:
        """Busca o artefato de uma data ou falha com 404."""
        artifact = self._artifacts.get_by_date(artifact_date)
        if artifact is None:
            raise ArtifactNotFoundError(
                f"Nenhum artefato registrado em {artifact_date.isoformat()}."
            )
        return artifact

    def get_random_artifact(self) -> Artifact:
        """Sorteia um artefato ou falha se a colecao estiver vazia."""
        artifact = self._artifacts.get_random()
        if artifact is None:
            raise EmptyCollectionError("Ainda nao ha artefatos registrados para sortear.")
        return artifact

    # ------------------------------------------------------------------
    # Escrita
    # ------------------------------------------------------------------

    def create_artifact(self, payload: ArtifactCreate) -> Artifact:
        """Registra o artefato do dia, respeitando as regras do dominio."""
        self._ensure_date_is_not_in_the_future(payload.artifact_date)
        self._ensure_date_is_free(payload.artifact_date)

        artifact = Artifact(
            artifact_date=payload.artifact_date,
            type=payload.type,
            title=payload.title,
            content=payload.content,
            url=payload.url,
            tags=self._resolve_tags(payload.tags),
        )
        return self._artifacts.create(artifact)

    def update_artifact(self, artifact_id: int, payload: ArtifactUpdate) -> Artifact:
        """Substitui por completo um artefato existente."""
        artifact = self.get_artifact(artifact_id)

        self._ensure_date_is_not_in_the_future(payload.artifact_date)
        if payload.artifact_date != artifact.artifact_date:
            self._ensure_date_is_free(payload.artifact_date)

        artifact.artifact_date = payload.artifact_date
        artifact.type = payload.type
        artifact.title = payload.title
        artifact.content = payload.content
        artifact.url = payload.url
        artifact.tags = self._resolve_tags(payload.tags)

        return self._artifacts.update(artifact)

    def delete_artifact(self, artifact_id: int) -> None:
        """Remove um artefato existente."""
        self._artifacts.delete(self.get_artifact(artifact_id))

    # ------------------------------------------------------------------
    # Regras internas
    # ------------------------------------------------------------------

    def _ensure_date_is_not_in_the_future(self, artifact_date: date) -> None:
        """Um dia so pode ser registrado depois de ter acontecido."""
        if artifact_date > date.today():
            raise FutureDateError(
                "Nao e possivel registrar um artefato em uma data futura."
            )

    def _ensure_date_is_free(self, artifact_date: date) -> None:
        """Garante a regra de um unico artefato por dia."""
        if self._artifacts.get_by_date(artifact_date) is not None:
            raise DuplicateDateError(
                f"Ja existe um artefato registrado em {artifact_date.isoformat()}."
            )

    def _resolve_tags(self, names: list[str]) -> list:
        """Normaliza os nomes recebidos e devolve as entidades Tag correspondentes."""
        normalized: list[str] = []
        for name in names:
            tag = self._normalize_tag(name)
            if tag and tag not in normalized:
                normalized.append(tag)
        return self._tags.get_or_create_many(normalized[:MAX_TAGS])

    @staticmethod
    def _normalize_tag(name: str | None) -> str | None:
        """Remove espacos das bordas e padroniza em minusculas."""
        if name is None:
            return None
        return name.strip().lower() or None
