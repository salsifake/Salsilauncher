from pydantic import BaseModel
from typing import Optional


class Colecao(BaseModel):
    id: str
    nome: str
    capa: Optional[str] = None
    descricao: Optional[str] = None

    @validator("id")
    def validar_id(cls, v):
        if " " in v:
            raise ValueError("O ID da coleção não pode conter espaços.")
        return v.lower()
