from PIL import Image
from pathlib import Path

def save_webp_image(input_file, output_path: Path, size=(600, 900), quality=85):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.open(input_file)
    img.thumbnail(size)
    img.save(output_path, "webp", quality=quality)

    return str(output_path)
