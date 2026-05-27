from urllib.parse import urlparse

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from .models import Project


def validate_github_url(value: str):
    if not value:
        return
    URLValidator()(value)
    host = (urlparse(value).hostname or "").lower()
    if host not in {"github.com", "www.github.com"}:
        raise ValidationError("Ссылка должна вести на github.com")


class ProjectForm(forms.ModelForm):
    github_url = forms.URLField(required=False, validators=[validate_github_url])

    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]

