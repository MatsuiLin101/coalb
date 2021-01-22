from django.db import models


class AbstractModel(models.Model):
    name = models.CharField(max_length=255, verbose_name="名稱")
    value = models.CharField(max_length=255, null=True, blank=True, verbose_name="值")

    class Meta:
        verbose_name = "抽象模型"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.id}"


class ProduceValueCity(AbstractModel):
    province = models.CharField(max_length=20, null=True, blank=True, verbose_name="省")

    class Meta:
        verbose_name = "產值表-城市"
        verbose_name_plural = verbose_name


class ProduceValueFarmCategory(AbstractModel):

    class Meta:
        verbose_name = "產值表-類別"
        verbose_name_plural = verbose_name


class ProduceValueProduct(AbstractModel):
    category = models.CharField(max_length=50, verbose_name="分組類別")

    class Meta:
        verbose_name = "產值表-產品"
        verbose_name_plural = verbose_name
