from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON
from backend.db.models.colecao import Colecao, ColecaoJogoLink


class Jogo(SQLModel, table=True):
    __tablename__ = "jogos"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        index=True
    )

    nome: str = Field(index=True)

    descricao: Optional[str] = None

    caminho_executavel: str
    caminho_pasta: str = Field(index=True)

    capa: Optional[str] = None
    fundo: Optional[str] = None

    imagens_extras: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON)
    )

    tags: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON)
    )

    horas_jogadas: int = 0
    favorito: bool = False

    colecoes: List["Colecao"] = Relationship(
        back_populates="jogos",
        link_model=ColecaoJogoLink
    )
