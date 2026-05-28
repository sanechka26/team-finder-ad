import io
import random

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from common.constants import (
    AVATAR_BG_COLORS,
    AVATAR_DEFAULT_LETTER,
    AVATAR_FONT_NAMES,
    AVATAR_FONT_SCALE,
    AVATAR_SIZE,
    AVATAR_TEXT_COLOR,
    AVATAR_VERTICAL_OFFSET_RATIO,
)


def _pick_avatar_bg() -> tuple[int, int, int]:
    return random.choice(AVATAR_BG_COLORS)


def generate_avatar_png(letter: str, size: int = AVATAR_SIZE) -> ContentFile:
    bg = _pick_avatar_bg()
    img = Image.new("RGB", (size, size), color=bg)
    draw = ImageDraw.Draw(img)

    letter = (letter or AVATAR_DEFAULT_LETTER).strip()[:1].upper()

    font = None
    font_size = int(size * AVATAR_FONT_SCALE)
    for font_name in AVATAR_FONT_NAMES:
        try:
            font = ImageFont.truetype(font_name, font_size)
            break
        except OSError:
            continue
    if font is None:
        font = ImageFont.load_default(size=font_size)

    bbox = draw.textbbox((0, 0), letter, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (size - w) / 2
    y = (size - h) / 2 - size * AVATAR_VERTICAL_OFFSET_RATIO
    draw.text((x, y), letter, fill=AVATAR_TEXT_COLOR, font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return ContentFile(buf.getvalue())
