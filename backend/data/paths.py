from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
MEDIA_DIR = BASE_DIR / "midia_launcher"

def ensure_media_dir():
    MEDIA_DIR.mkdir(exist_ok=True)

def get_capa_path(jogo_id: int) -> Path:
    ensure_media_dir()
    return MEDIA_DIR / f"{jogo_id}_capa.webp"

def get_fundo_path(jogo_id: int) -> Path:
    ensure_media_dir()
    return MEDIA_DIR / f"{jogo_id}_fundo.webp"

def get_extra_image_path(jogo_id: int, index: int) -> Path:
    ensure_media_dir()
    return MEDIA_DIR / f"{jogo_id}_extra_{index}.webp"
