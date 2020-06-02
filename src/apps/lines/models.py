from django.db import models


class LineUser(models.Model):
    userId = models.CharField(max_length=255, null=True, blank=True, verbose_name="識別碼")
    displayName = models.CharField(max_length=255, null=True, blank=True, verbose_name="顯示名稱")
    pictureUrl = models.CharField(max_length=255, null=True, blank=True, verbose_name="大頭貼")
    statusMessage = models.CharField(max_length=255, null=True, blank=True, verbose_name="狀態")
    language = models.CharField(max_length=20, default="zh-Hant", null=True, blank=True, verbose_name="語言")
    status = models.BooleanField(default=False, null=True, blank=True, verbose_name="狀態")

    class Meta:
        verbose_name = "Line使用者"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id


class SD(models.Model):
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    layer = models.CharField(max_length=2, blank=True, null=True, default=None)
    parent = models.ForeignKey("self", blank=True, null=True, default=None, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.value} - {self.layer}"

    def save(self, *args, **kwargs):
        if self.pk is None:
            obj = SD.objects.filter(name=self.name, value=self.value, layer=self.layer, parent=self.parent)
            if not obj:
                print(f"Create {self.name}, {self.value}, {self.layer}, {self.parent}")
                super(SD, self).save(*args, **kwargs)
            else:
                print(f"Exist {self.name}, {self.value}, {self.layer}, {self.parent}")
        else:
            super(SD, self).save(*args, **kwargs)
