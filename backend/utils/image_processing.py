from PIL import Image, UnidentifiedImageError
from fastapi import UploadFile, HTTPException
import io
from pathlib import Path

def save_webp_image(input_file, output_path: Path, size=(600, 900), quality=85):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.open(input_file)
    img.thumbnail(size)
    img.save(output_path, "webp", quality=quality)

    return str(output_path)

def validate_image_upload(file: UploadFile):
    """
    Validação mínima de imagem
    Garante que:
    - content-type é imagem
    - arquivo é uma imagem válida
    """

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Arquivo enviado não é uma imagem."
        )

    try:
        raw = file.file.read()
        image = Image.open(io.BytesIO(raw))
        image.verify()  # valida
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="Imagem inválida ou corrompida."
        )
    finally:
        # Resetar ponteiro para reutilizar depois
        file.file.seek(0)
