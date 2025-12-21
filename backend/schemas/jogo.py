from typing import List, Optional
from pydantic import BaseModel, Field


class JogoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    desenvolvedor: Optional[str] = None
    studio: Optional[str] = None
    tags: List[str] = []
    colecoes: List[str] = []
    links: List[dict] = []


class JogoCreate(JogoBase):
    caminho_executavel: Optional[str] = None
    caminho_pasta: Optional[str] = None


class JogoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    desenvolvedor: Optional[str] = None
    studio: Optional[str] = None
    tags: Optional[List[str]] = None
    colecoes: Optional[List[str]] = None
    links: Optional[List[dict]] = None
    caminho_executavel: Optional[str] = None
    caminho_pasta: Optional[str] = None


class JogoRead(JogoBase):
    id: int

    caminho_executavel: Optional[str] = None
    caminho_pasta: Optional[str] = None

    imagem_capa: Optional[str] = None
    imagem_fundo: Optional[str] = None
    imagens_extras: List[str] = []

    class Config:
        from_attributes = True
