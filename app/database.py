"""Configuracao do SQLAlchemy e da sessao de banco de dados."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# check_same_thread=False e necessario porque o SQLite e acessado por
# threads diferentes do pool do Uvicorn.
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Classe base de todos os modelos ORM."""


def get_db() -> Iterator[Session]:
    """Dependencia do FastAPI que fornece uma sessao por requisicao."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Cria o arquivo SQLite e as tabelas, caso ainda nao existam."""
    from app import models  # noqa: F401  (registra os modelos no metadata)

    Base.metadata.create_all(bind=engine)
