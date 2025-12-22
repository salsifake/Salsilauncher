from pydantic import BaseModel
from typing import List

class ColecaoCreate(BaseModel):
    nome: str
    jogos: List[int] = []
