from pydantic import BaseModel, Field
from typing import List, Optional

from .AvaliacaoDetalhada import AvaliacaoDetalhada
from .Links import Link


class Jogo(BaseModel):
    id: int

    # Informações gerais
    nome: str
    descricao: Optional[str] = None
    genero: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    # Caminhos e arquivos
    caminho_executavel: str
    caminho_pasta: str
    imagem_capa: Optional[str] = None
    imagem_fundo: Optional[str] = None
    imagens_extras: List[str] = Field(default_factory=list)

    # Metadados técnicos
    tamanho_gb: Optional[float] = None
    desenvolvedor: Optional[str] = None
    studio: Optional[str] = None
    engine: Optional[str] = None
    versao: Optional[str] = None

    # Links
    links: List[Link] = Field(default_factory=list)

    # Coleções a que o jogo pertence (apenas IDs de coleções)
    colecoes: List[str] = Field(default_factory=list)

    # Progresso e estado do jogador
    tempo_jogado_segundos: int = 0
    ultima_vez_jogado: Optional[str] = None
    status: str = "Não Jogado"
    zerado: bool = False
    jogar_mais_tarde: bool = False

    # Avaliação
    review_texto: Optional[str] = None
    avaliacao_detalhada: Optional[AvaliacaoDetalhada] = None
