from django.db import models


class LineBodyLog(models.Model):
    user = models.ForeignKey("line.LineUser", on_delete=models.CASCADE, verbose_name="LINE使用者")
    body = models.TextField(verbose_name="接收內容")
    created = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")

    class Meta:
        verbose_name = "LINE接收訊息記錄"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user}"
