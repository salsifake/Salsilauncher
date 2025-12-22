import json
import os
import tempfile
from pathlib import Path
from filelock import FileLock
from typing import Any, List


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
TMP_DIR = BASE_DIR / "tmp"

DATA_DIR.mkdir(exist_ok=True)
TMP_DIR.mkdir(exist_ok=True)

JOGOS_DB = DATA_DIR / "jogos_db.json"
COLECOES_DB = DATA_DIR / "colecoes_db.json"

LOCK_JOGOS = FileLock(str(JOGOS_DB) + ".lock")
LOCK_COLECOES = FileLock(str(COLECOES_DB) + ".lock")

JOGOS_META = DATA_DIR / "jogos_meta.json"
COLECOES_META = DATA_DIR / "colecoes_meta.json"


# --- Funções auxiliares ---

def _atomic_write(path: Path, data: Any):
    """Escreve JSON de forma atômica usando arquivo temporário + os.replace()."""
    with tempfile.NamedTemporaryFile(
        "w",
        delete=False,
        dir=TMP_DIR,
        encoding="utf-8"
    ) as tmp:
        json.dump(data, tmp, ensure_ascii=False, indent=2)
        temp_name = tmp.name

    os.replace(temp_name, path)


def _safe_load(path: Path):
    """Carrega JSON de forma segura com tratamento explícito."""
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        backup_path = path.with_suffix(".broken.json")
        os.replace(path, backup_path)
        raise RuntimeError(
            f"Arquivo corrompido detectado. Backup movido para {backup_path}"
        )


# --- API pública ---

def carregar_jogos() -> List[dict]:
    with LOCK_JOGOS:
        return _safe_load(JOGOS_DB)


def salvar_jogos(jogos: List[dict]):
    with LOCK_JOGOS:
        _atomic_write(JOGOS_DB, jogos)


def carregar_colecoes() -> List[dict]:
    with LOCK_COLECOES:
        return _safe_load(COLECOES_DB)


def salvar_colecoes(colecoes: List[dict]):
    with LOCK_COLECOES:
        _atomic_write(COLECOES_DB, colecoes)

def next_id(meta_path: Path) -> int:
    lock = FileLock(str(meta_path) + ".lock")

    with lock:
        if not meta_path.exists():
            data = {"last_id": 0}
        else:
            data = _safe_load(meta_path)

        data["last_id"] += 1
        _atomic_write(meta_path, data)

        return data["last_id"]
