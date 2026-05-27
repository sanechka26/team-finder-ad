from django import forms
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError

from .models import User, normalize_phone, validate_github_url, validate_phone


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password"]

    def clean_password(self):
        password = self.cleaned_data.get("password") or ""
        password_validation.validate_password(password)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        # phone is required by model; but registration form doesn't ask it.
        # Set a temporary unique value; user can change it later in profile edit.
        # (Templates in variant 1 do not ask phone on register.)
        if not user.phone:
            user.phone = self._generate_temp_phone()
        if commit:
            user.save()
        return user

    def _generate_temp_phone(self) -> str:
        # Generate a unique phone matching validation (+7XXXXXXXXXX).
        # Users are expected to set a real phone later in profile edit.
        while True:
            num = "+7" + f"{User.objects.count():010d}"
            if not User.objects.filter(phone=num).exists():
                return num


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")
        if not email or not password:
            return cleaned
        user = authenticate(username=email, password=password)
        if user is None:
            raise ValidationError("Неверный email или пароль")
        if not user.is_active:
            raise ValidationError("Пользователь заблокирован")
        cleaned["user"] = user
        return cleaned


class ProfileEditForm(forms.ModelForm):
    phone = forms.CharField(required=False)
    github_url = forms.URLField(required=False)

    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]

    def clean_phone(self):
        phone = self.cleaned_data.get("phone") or ""
        phone = phone.strip()
        if not phone:
            return phone
        validate_phone(phone)
        phone = normalize_phone(phone)
        qs = User.objects.filter(phone=phone)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Этот номер телефона уже используется")
        return phone

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url") or ""
        if not url:
            return url
        validate_github_url(url)
        return url


class ChangePasswordForm(PasswordChangeForm):
    # Keep Django built-in validation/error messages.
    pass

