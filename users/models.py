from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from common.constants import (
    AVATAR_DEFAULT_LETTER,
    USER_ABOUT_MAX_LENGTH,
    USER_NAME_MAX_LENGTH,
    USER_PHONE_MAX_LENGTH,
)
from common.validators import normalize_phone, validate_github_url, validate_phone

from .managers import UserManager
from .service import generate_avatar_png


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    phone = models.CharField(
        max_length=USER_PHONE_MAX_LENGTH,
        unique=True,
        validators=[validate_phone],
    )
    github_url = models.URLField(blank=True, validators=[validate_github_url])
    about = models.CharField(max_length=USER_ABOUT_MAX_LENGTH, blank=True)
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
            letter = self.name[:1] if self.name else AVATAR_DEFAULT_LETTER
            content = generate_avatar_png(letter)
            filename = f"user_{self.pk}_avatar.png"
            self.avatar.save(filename, content, save=True)

    def __str__(self) -> str:
        return self.email



