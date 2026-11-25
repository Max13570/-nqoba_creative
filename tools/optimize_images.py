"""
Resize and convert images so the website loads fast.

Usage (from the project folder):
    python tools/optimize_images.py  path/to/input_folder  path/to/output_folder

* Converts CMYK to RGB (browsers show CMYK JPEGs with wrong colours).
* Shrinks anything wider than 1400 px.
* Saves as JPEG (quality 85), usually 100 to 300 KB per image.
"""

import sys
from pathlib import Path

from PIL import Image, ImageOps

MAX_WIDTH = 1400
EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp'}


def optimize(source, target):
    with Image.open(source) as image:
        if image.format == 'JPEG':
            # Lets Pillow decode huge JPEGs at reduced size (fast, low memory)
            image.draft(image.mode, (MAX_WIDTH * 2, MAX_WIDTH * 2))

        image = ImageOps.exif_transpose(image)

        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, 'white')
            rgba = image.convert('RGBA')
            background.paste(rgba, mask=rgba.split()[-1])
            image = background
        else:
            image = image.convert('RGB')

        if image.width > MAX_WIDTH:
            height = round(image.height * MAX_WIDTH / image.width)
            image = image.resize((MAX_WIDTH, height), Image.LANCZOS)

        image.save(target, 'JPEG', quality=85, optimize=True, progressive=True)


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    source_dir, target_dir = Path(sys.argv[1]), Path(sys.argv[2])
    target_dir.mkdir(parents=True, exist_ok=True)

    for source in sorted(source_dir.iterdir()):
        if source.suffix.lower() not in EXTENSIONS:
            continue

        target = target_dir / (source.stem + '.jpg')
        optimize(source, target)

        before = source.stat().st_size / 1024
        after = target.stat().st_size / 1024
        print(f'{source.name}: {before:,.0f} KB -> {after:,.0f} KB')


if __name__ == '__main__':
    main()
