import datetime

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    fullname = models.CharField(max_length=20, verbose_name="顯示名稱")
    line_uid = models.CharField(max_length=255, verbose_name="Line識別碼")
    allowed_upload = models.BooleanField(default=False, verbose_name="是否允許上傳檔案")

    class Meta:
        verbose_name = '使用者'
        verbose_name_plural = verbose_name

    def set_password(self, password=None):
        if password is None:
            manager = BaseUserManager()
            password = manager.make_random_password()
        super(CustomUser, self).set_password(password)
        return password

    def __str__(self):
        return f"{self.username}"


class CustomSetting(models.Model):
    name = models.CharField(max_length=255, verbose_name="名稱")
    value = models.CharField(max_length=255, verbose_name="值")

    class Meta:
        verbose_name = '特殊設定'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name}"


class DatabaseControl(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="上傳者")
    name = models.CharField(max_length=50, verbose_name="資料庫名稱")
    status = models.BooleanField(default=False, verbose_name="狀態")
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="開始時間")
    finish_time = models.DateTimeField(blank=True, null=True, verbose_name="結束時間")
    expire_time = models.DateTimeField(default=timezone.now() + datetime.timedelta(0, 600), verbose_name="過期時間")

    class Meta:
        verbose_name = '資料庫鎖定'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name}"
