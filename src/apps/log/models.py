from django.db import models


class LineCallBackLog(models.Model):
    signature = models.CharField(max_length=255, verbose_name="簽名")
    body = models.TextField(verbose_name="內容")
    message = models.TextField(verbose_name="錯誤訊息")
    created = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")

    class Meta:
        verbose_name = "LINE掛勾錯誤記錄"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.id}"


class LineBodyLog(models.Model):
    user = models.ForeignKey("line.LineUser", on_delete=models.CASCADE, verbose_name="LINE使用者")
    body = models.TextField(verbose_name="接收內容")
    created = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")

    class Meta:
        verbose_name = "LINE接收訊息記錄"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user}"


class LineMessageLog(models.Model):
    user = models.ForeignKey("line.LineUser", on_delete=models.CASCADE, verbose_name="LINE使用者")
    message_id = models.CharField(max_length=64, verbose_name="訊息識別碼")
    reply_token = models.CharField(max_length=64, verbose_name="回應字段")
    message = models.TextField(verbose_name="訊息內容")
    reply = models.TextField(verbose_name="回應內容")
    status = models.BooleanField(default=True, verbose_name="狀態")
    created = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    timestamp = models.FloatField(blank=True, null=True, verbose_name="請求時間戳")
    method = models.CharField(max_length=10, default="reply", verbose_name="回應方式")
    reply_at = models.DateTimeField(auto_now=True, verbose_name="回應時間")

    class Meta:
        verbose_name = "LINE文字訊息記錄"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user}"


class LineFollowLog(models.Model):
    user = models.ForeignKey("line.LineUser", on_delete=models.CASCADE, verbose_name="LINE使用者")
    reply_token = models.CharField(max_length=64, null=True, blank=True, verbose_name="回應字段")
    message = models.CharField(max_length=10, verbose_name="好友狀態")
    reply = models.TextField(verbose_name="錯誤訊息")
    status = models.BooleanField(default=True, verbose_name="狀態")
    created = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")

    class Meta:
        verbose_name = "LINE好友狀態記錄"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user}"


class TracebackLog(models.Model):
    app = models.CharField(max_length=255, verbose_name="關聯app")
    message = models.TextField(verbose_name="錯誤訊息")
    created = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")

    class Meta:
        verbose_name = "例外報錯記錄"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.app}"
