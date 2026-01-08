from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from backend.db.models.jogo import ColecaoJogoLink


if TYPE_CHECKING:
    from backend.db.models.jogo import Jogo

class Colecao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str

    jogos: List["Jogo"] = Relationship(
        back_populates="colecoes",
        link_model=ColecaoJogoLink
    )
