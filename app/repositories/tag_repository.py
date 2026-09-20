"""Acesso ao banco para a entidade Tag."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tag import Tag


class TagRepository:
    """Persistencia de tags, reaproveitando as que ja existem."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_or_create_many(self, names: list[str]) -> list[Tag]:
        """Retorna as tags dos nomes informados, criando apenas as inexistentes.

        Espera nomes ja normalizados pelo service (sem espacos e em minusculas).
        """
        if not names:
            return []

        existing = self._db.scalars(select(Tag).where(Tag.name.in_(names))).all()
        by_name = {tag.name: tag for tag in existing}

        for name in names:
            if name not in by_name:
                tag = Tag(name=name)
                self._db.add(tag)
                by_name[name] = tag

        # Preserva a ordem em que as tags foram informadas.
        return [by_name[name] for name in names]
