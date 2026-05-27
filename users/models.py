import io
import random

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models

from PIL import Image, ImageDraw, ImageFont

from common.constants import AVATAR_BG_COLORS, USER_NAME_MAX_LENGTH
from common.validators import normalize_phone, validate_github_url, validate_phone

from .managers import UserManager


def _pick_avatar_bg() -> tuple[int, int, int]:
    return random.choice(AVATAR_BG_COLORS)


def generate_avatar_png(letter: str, size: int = 256) -> ContentFile:
    bg = _pick_avatar_bg()
    img = Image.new("RGB", (size, size), color=bg)
    draw = ImageDraw.Draw(img)

    letter = (letter or "U").strip()[:1].upper()

    # Try to load a truetype font; fallback to default.
    font = None
    for font_name in ("arial.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"):
        try:
            font = ImageFont.truetype(font_name, int(size * 0.55))
            break
        except OSError:
            continue
    if font is None:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), letter, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (size - w) / 2
    y = (size - h) / 2 - size * 0.03
    draw.text((x, y), letter, fill=(255, 255, 255), font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return ContentFile(buf.getvalue())


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    phone = models.CharField(max_length=12, unique=True, validators=[validate_phone])
    github_url = models.URLField(blank=True, validators=[validate_github_url])
    about = models.CharField(max_length=256, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname", "phone"]

    class Meta:
        pass

    def clean(self):
        super().clean()
        if self.phone:
            self.phone = normalize_phone(self.phone)

    def save(self, *args, **kwargs):
        if self.phone:
            self.phone = normalize_phone(self.phone)

        generating_avatar = self.pk is None and not self.avatar
        super().save(*args, **kwargs)

        # Generate avatar after first save to have a pk for filename.
        if generating_avatar and not self.avatar:
            content = generate_avatar_png(self.name[:1] if self.name else "U")
            filename = f"user_{self.pk}_avatar.png"
            self.avatar.save(filename, content, save=True)

    def __str__(self) -> str:
        return self.email



