from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    fullname = models.CharField(max_length=20, verbose_name="顯示名稱")

    class Meta:
        verbose_name = '使用者'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.username}"
