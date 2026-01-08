from typing import List, Optional
from sqlmodel import Session, select
from sqlalchemy.sql import func

from ..models.jogo import Jogo


def listar_jogos(
    session: Session,
    *,
    offset: int = 0,
    limit: int = 100
) -> List[Jogo]:
    statement = (
        select(Jogo)
        .offset(offset)
        .limit(limit)
    )
    return session.exec(statement).all()


def buscar_jogos_por_tags(
    session: Session,
    tags: set[str],
    *,
    offset: int = 0,
    limit: int = 100
) -> List[Jogo]:
    # tags armazenadas como JSON → filtro em Python (por enquanto)
    jogos = listar_jogos(session, offset=offset, limit=limit)
    return [
        j for j in jogos
        if tags.issubset({t.lower() for t in j.tags})
    ]


def obter_jogo_por_id(
    session: Session,
    jogo_id: int
) -> Optional[Jogo]:
    return session.get(Jogo, jogo_id)


def criar_jogo(
    session: Session,
    jogo: Jogo
) -> Jogo:
    session.add(jogo)
    session.commit()
    session.refresh(jogo)
    return jogo


def atualizar_jogo(
    session: Session,
    jogo: Jogo
) -> Jogo:
    session.add(jogo)
    session.commit()
    session.refresh(jogo)
    return jogo


def remover_jogo(
    session: Session,
    jogo: Jogo
):
    session.delete(jogo)
    session.commit()


def jogos_aleatorios(
    session: Session,
    *,
    limit: int = 5
) -> List[Jogo]:
    statement = (
        select(Jogo)
        .order_by(func.random())
        .limit(limit)
    )
    return session.exec(statement).all()
