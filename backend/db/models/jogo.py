from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

if TYPE_CHECKING:
    from backend.db.models.colecao import Colecao

class ColecaoJogoLink(SQLModel, table=True):
    colecao_id: int | None = Field(
        default=None,
        foreign_key="colecao.id",
        primary_key=True
    )
    jogo_id: int | None = Field(
        default=None,
        foreign_key="jogo.id",
        primary_key=True
    )

class Jogo(SQLModel, table=True):
    __tablename__ = "jogo"

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
