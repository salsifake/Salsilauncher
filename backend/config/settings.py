from pathlib import Path
import os
from functools import lru_cache
from typing import List


BASE_DIR = Path(__file__).resolve().parent.parent


@lru_cache
def get_settings():
    """
    Configurações centrais do backend.
    Não executa side-effects (não cria pasta, não abre arquivo).
    """

    # --- CORS ---
    origins_env = os.getenv("ALLOWED_ORIGINS", "").strip()

    if origins_env:
        allowed_origins: List[str] = [
            o.strip() for o in origins_env.split(",") if o.strip()
        ]
    else:
        # defaults para desenvolvimento
        allowed_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]

    # --- Diretórios de runtime ---
    data_dir = Path(os.getenv("DATA_DIR", BASE_DIR))

    media_dir = Path(
        os.getenv("MIDIA_DIR", data_dir / "midia_launcher")
    )

    return {
        "BASE_DIR": BASE_DIR,
        "DATA_DIR": data_dir,
        "MIDIA_DIR": media_dir,
        "ALLOWED_ORIGINS": allowed_origins,
    }
