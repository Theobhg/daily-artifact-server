"""Rotas HTTP dos artefatos diarios."""

from datetime import date

from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.artifact import Artifact, ArtifactType
from app.schemas.artifact import ArtifactCreate, ArtifactResponse, ArtifactUpdate
from app.services.artifact_service import ArtifactService

router = APIRouter(prefix="/artifacts", tags=["artifacts"])

NOT_FOUND = {"description": "Artefato nao encontrado."}
CONFLICT = {"description": "Ja existe um artefato registrado nesta data."}
FUTURE_DATE = {"description": "A data informada esta no futuro."}
VALIDATION = {"description": "Payload invalido para o tipo de artefato informado."}


def get_service(db: Session = Depends(get_db)) -> ArtifactService:
    """Fornece o service ja ligado a sessao da requisicao."""
    return ArtifactService(db)


@router.post(
    "",
    response_model=ArtifactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar o artefato de um dia",
    description=(
        "Cria o unico artefato permitido para a data informada.\n\n"
        "Artefatos do tipo `text` e `quote` exigem `content`; os tipos `photo`, "
        "`link` e `music` exigem `url`. Datas futuras sao recusadas e cada data "
        "aceita no maximo um artefato."
    ),
    responses={400: FUTURE_DATE, 409: CONFLICT, 422: VALIDATION},
)
def create_artifact(
    payload: ArtifactCreate,
    service: ArtifactService = Depends(get_service),
) -> Artifact:
    return service.create_artifact(payload)


@router.get(
    "",
    response_model=list[ArtifactResponse],
    summary="Listar artefatos",
    description=(
        "Retorna os artefatos do mais recente para o mais antigo.\n\n"
        "Os filtros sao opcionais e combinaveis, por exemplo "
        "`/artifacts?year=2026&type=photo`."
    ),
)
def list_artifacts(
    type: ArtifactType | None = Query(default=None, description="Filtra por tipo de artefato."),
    year: int | None = Query(default=None, ge=1900, le=2999, description="Filtra por ano."),
    month: int | None = Query(default=None, ge=1, le=12, description="Filtra por mes (1 a 12)."),
    tag: str | None = Query(default=None, description="Filtra por tag (case-insensitive)."),
    service: ArtifactService = Depends(get_service),
) -> list[Artifact]:
    return service.list_artifacts(type=type, year=year, month=month, tag=tag)


# As rotas literais abaixo precisam vir antes de /artifacts/{artifact_id}
# para nao serem capturadas pela rota parametrizada.


@router.get(
    "/random",
    response_model=ArtifactResponse,
    summary="Sortear um artefato",
    description=(
        "Retorna um artefato aleatorio da colecao. Alimenta a funcionalidade "
        "*Me surpreenda*. Responde `404` quando ainda nao ha nada registrado."
    ),
    responses={404: {"description": "A colecao ainda esta vazia."}},
)
def get_random_artifact(
    service: ArtifactService = Depends(get_service),
) -> Artifact:
    return service.get_random_artifact()


@router.get(
    "/by-date/{artifact_date}",
    response_model=ArtifactResponse,
    summary="Buscar o artefato de uma data",
    description=(
        "Retorna o artefato registrado na data informada, no formato ISO "
        "`YYYY-MM-DD`. Responde `404` quando aquele dia ainda nao foi registrado."
    ),
    responses={404: NOT_FOUND},
)
def get_artifact_by_date(
    artifact_date: date = Path(description="Data no formato ISO (YYYY-MM-DD)."),
    service: ArtifactService = Depends(get_service),
) -> Artifact:
    return service.get_artifact_by_date(artifact_date)


@router.get(
    "/{artifact_id}",
    response_model=ArtifactResponse,
    summary="Buscar um artefato por id",
    description="Retorna um unico artefato a partir do seu identificador.",
    responses={404: NOT_FOUND},
)
def get_artifact(
    artifact_id: int = Path(ge=1, description="Identificador do artefato."),
    service: ArtifactService = Depends(get_service),
) -> Artifact:
    return service.get_artifact(artifact_id)


@router.put(
    "/{artifact_id}",
    response_model=ArtifactResponse,
    summary="Atualizar um artefato",
    description=(
        "Substitui por completo os dados de um artefato, incluindo suas tags.\n\n"
        "As mesmas regras da criacao continuam valendo: datas futuras sao "
        "recusadas e mover o artefato para uma data ja ocupada gera conflito."
    ),
    responses={400: FUTURE_DATE, 404: NOT_FOUND, 409: CONFLICT, 422: VALIDATION},
)
def update_artifact(
    payload: ArtifactUpdate,
    artifact_id: int = Path(ge=1, description="Identificador do artefato."),
    service: ArtifactService = Depends(get_service),
) -> Artifact:
    return service.update_artifact(artifact_id, payload)


@router.delete(
    "/{artifact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir um artefato",
    description="Remove o artefato e libera a data para um novo registro.",
    responses={404: NOT_FOUND},
)
def delete_artifact(
    artifact_id: int = Path(ge=1, description="Identificador do artefato."),
    service: ArtifactService = Depends(get_service),
) -> Response:
    service.delete_artifact(artifact_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
