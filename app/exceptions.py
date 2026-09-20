"""Excecoes de dominio da Daily Artifact API.

O service levanta estas excecoes sem conhecer HTTP. A traducao para respostas
HTTP acontece em um unico lugar (app/main.py), mantendo os routers enxutos.
"""


class DomainError(Exception):
    """Erro de regra de negocio. status_code define a resposta HTTP."""

    status_code: int = 400

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class ArtifactNotFoundError(DomainError):
    """Nenhum artefato encontrado para o identificador ou data informados."""

    status_code = 404


class DuplicateDateError(DomainError):
    """Ja existe um artefato registrado na data informada."""

    status_code = 409


class FutureDateError(DomainError):
    """A data informada esta no futuro."""

    status_code = 400


class EmptyCollectionError(DomainError):
    """A colecao esta vazia e nao ha artefato para sortear."""

    status_code = 404
