import secrets

from django.conf import settings
from django.db import models


class AuthToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='auth_tokens',
    )
    key = models.CharField(max_length=256, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(128)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Token for {self.user.username}"
