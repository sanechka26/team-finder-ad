from django import forms

from common.validators import validate_github_url

from .models import Project


class ProjectForm(forms.ModelForm):
    github_url = forms.URLField(required=False, validators=[validate_github_url])

    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]

