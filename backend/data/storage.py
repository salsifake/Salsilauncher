# backend/data/storage.py
import json
import os
import tempfile
import shutil
from typing import Any

def salvar_arquivo_atomico(path: str, dados: Any, *, ensure_ascii: bool = False, indent: int = 4) -> None:
    """
    Salva 'dados' (serializáveis em JSON) no arquivo 'path' de forma atômica:
    - escreve em um arquivo temporário na mesma pasta;
    - depois substitui o original com move (atomic on most OS).
    """
    dir_path = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(dir_path, exist_ok=True)

    # mkstemp cria um fd aberto; fechamos para usar open normal
    fd, tmp_path = tempfile.mkstemp(prefix=".tmp_", dir=dir_path)
    os.close(fd)

    try:
        # gravar no temporário
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=ensure_ascii, indent=indent)
            f.flush()
            os.fsync(f.fileno())  # garante escrita física quando possível

        # substituir (move) — em geral atômico na mesma filesystem
        # shutil.move usa os.rename internamente quando possível
        shutil.move(tmp_path, path)
    except Exception:
        # cleanup: tenta remover o arquivo temporário se existir
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        raise

def ler_json_seguro(path: str, default: Any = None) -> Any:
    """
    Lê um JSON de forma segura:
    - se o arquivo não existir -> retorna default
    - se JSON estiver corrompido -> retorna default (não sobrescreve)
    """
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # arquivo corrompido — não sobrescrever automaticamente
        return default

def remover_arquivo(path: str) -> None:
    """Remove um arquivo se existir (silencioso)."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass
