from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def remover_assets_jogo(jogo):
    paths = []

    if getattr(jogo, "capa", None):
        paths.append(jogo.capa)

    if getattr(jogo, "fundo", None):
        paths.append(jogo.fundo)

    if getattr(jogo, "imagens_extras", None):
        paths.extend(jogo.imagens_extras)

    for p in paths:
        try:
            path = Path(p)
            if path.exists():
                path.unlink()
        except Exception as e:
            logger.warning(
                "Falha ao remover asset %s: %s", p, e)
