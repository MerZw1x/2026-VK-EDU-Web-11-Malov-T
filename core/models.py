from django.db import models
from django.conf import settings

from pathlib import Path
from uuid import uuid4

def avatar_upload_path(instance, filename: str):
    extension = Path(filename).suffix.lower()
    part = uuid4().hex
    return "avatars/" + part + extension

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )
    nickname = models.CharField("Никнейм", max_length=40, blank=True)
    avatar = models.ImageField("Аватар", upload_to=avatar_upload_path, blank=True)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Профиль пользователя #{self.user_id}"