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
    """
    type 1 or 2:
    type 1: $LB0101
    type 2: $LB0201
    """
    province = models.CharField(max_length=20, null=True, blank=True, verbose_name="省")
    type = models.IntegerField(verbose_name="類型")

    class Meta:
        verbose_name = "產值表-城市"
        verbose_name_plural = verbose_name


class ProduceValueFarmCategory(AbstractModel):

    class Meta:
        verbose_name = "產值表-類別"
        verbose_name_plural = verbose_name


class ProduceValueProduct(AbstractModel):
    category = models.CharField(max_length=50, verbose_name="分組類別")
    city_type = models.IntegerField(verbose_name="城市類型")

    class Meta:
        verbose_name = "產值表-產品"
        verbose_name_plural = verbose_name
