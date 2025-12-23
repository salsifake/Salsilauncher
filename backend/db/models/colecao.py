from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from backend.db.models.jogo import Jogo


class ColecaoJogoLink(SQLModel, table=True):
    colecao_id: Optional[int] = Field(
        default=None,
        foreign_key="colecao.id",
        primary_key=True
    )
    jogo_id: Optional[int] = Field(
        default=None,
        foreign_key="jogo.id",
        primary_key=True
    )


class Colecao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str

    jogos: List["Jogo"] = Relationship(
        back_populates="colecoes",
        link_model=ColecaoJogoLink
    )
