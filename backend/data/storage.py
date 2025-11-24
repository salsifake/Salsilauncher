import os
import json
from typing import List, Any, Optional
from filelock import FileLock

from models.jogo import Jogo
from models.colecao import Colecao


# -----------------------------
# Funções utilitárias
# -----------------------------

def salvar_arquivo_atomico(caminho: str, dados: Any):
    """
    Salva um arquivo JSON de forma atômica para evitar corrupção
    caso o programa seja interrompido durante escrita.
    """
    temp = caminho + ".tmp"

    with open(temp, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

    os.replace(temp, caminho)


def ler_json_seguro(caminho: str, default: Optional[Any] = None):
    """
    Lê um JSON com tratamento de erros.
    Se o arquivo estiver corrompido ou não existir, retorna default.
    """
    if not os.path.exists(caminho):
        return default

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


# -----------------------------
# Jogos
# -----------------------------

DB_FILE = "jogos_db.json"

def salvar_jogos(jogos: List[Jogo]):
    lock = FileLock(DB_FILE + ".lock")
    with lock:
        dados = [j.dict() for j in jogos]
        salvar_arquivo_atomico(DB_FILE, dados)

def carregar_jogos() -> List[Jogo]:
    dados = ler_json_seguro(DB_FILE, default=[])
    return [Jogo(**j) for j in dados]


# -----------------------------
# Coleções
# -----------------------------

COLECOES_DB_FILE = "colecoes_db.json"

def salvar_colecoes(colecoes: List[Colecao]):
    dados = [c.dict() for c in colecoes]
    salvar_arquivo_atomico(COLECOES_DB_FILE, dados)

def carregar_colecoes() -> List[Colecao]:
    dados = ler_json_seguro(COLECOES_DB_FILE, default=None)

    if not dados:
        colecao_padrao = [Colecao(id="jogar-mais-tarde", nome="Jogar mais Tarde")]
        salvar_colecoes(colecao_padrao)
        return colecao_padrao

    return [Colecao(**c) for c in dados]
