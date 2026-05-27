from __future__ import annotations

import re
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


PHONE_RE = re.compile(r"^(8\d{10}|\+7\d{10})$")


def normalize_phone(value: str) -> str:
    value = (value or "").strip().replace(" ", "").replace("-", "")
    if value.startswith("8") and len(value) == 11:
        return "+7" + value[1:]
    return value


def validate_phone(value: str):
    value = normalize_phone(value)
    if not PHONE_RE.match(value):
        raise ValidationError("Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX")


def validate_github_url(value: str):
    if not value:
        return
    URLValidator()(value)
    host = (urlparse(value).hostname or "").lower()
    if host not in {"github.com", "www.github.com"}:
        raise ValidationError("Ссылка должна вести на github.com")

