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


class TotalValue(models.Model):
    parent = models.ForeignKey("TotalValue", on_delete=models.CASCADE, null=True, blank=True, verbose_name="上層物件")
    main_class = models.CharField(max_length=50, verbose_name="主分類")
    sub_class = models.CharField(max_length=50, verbose_name="次分類")
    level = models.PositiveIntegerField(verbose_name="級別")
    name = models.CharField(max_length=20, verbose_name="名稱")
    value = models.CharField(max_length=20, verbose_name="值")
    search_name = models.CharField(max_length=20, verbose_name="搜尋名稱")

    class Meta:
        verbose_name = "總產值"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.search_name}"


class LivestockFeedlot(models.Model):
    parent = models.ForeignKey("LivestockFeedlot", on_delete=models.CASCADE, null=True, blank=True, verbose_name="上層物件")
    main_class = models.CharField(max_length=50, verbose_name="主分類")
    sub_class = models.CharField(max_length=50, verbose_name="次分類")
    level = models.PositiveIntegerField(verbose_name="級別")
    name = models.CharField(max_length=20, verbose_name="名稱")
    value = models.CharField(max_length=20, verbose_name="值")
    search_name = models.CharField(max_length=20, verbose_name="搜尋名稱")

    class Meta:
        verbose_name = "畜禽飼養場數"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.search_name}"


class LivestockFeedamount(models.Model):
    parent = models.ForeignKey("LivestockFeedamount", on_delete=models.CASCADE, null=True, blank=True, verbose_name="上層物件")
    main_class = models.CharField(max_length=50, verbose_name="主分類")
    sub_class = models.CharField(max_length=50, verbose_name="次分類")
    level = models.PositiveIntegerField(verbose_name="級別")
    name = models.CharField(max_length=20, verbose_name="名稱")
    value = models.CharField(max_length=20, verbose_name="值")
    search_name = models.CharField(max_length=20, verbose_name="搜尋名稱")

    class Meta:
        verbose_name = "畜禽飼養頭數"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.search_name}"


class LivestockSlaughter(models.Model):
    parent = models.ForeignKey("LivestockSlaughter", on_delete=models.CASCADE, null=True, blank=True, verbose_name="上層物件")
    main_class = models.CharField(max_length=50, verbose_name="主分類")
    sub_class = models.CharField(max_length=50, verbose_name="次分類")
    level = models.PositiveIntegerField(verbose_name="級別")
    name = models.CharField(max_length=20, verbose_name="名稱")
    value = models.CharField(max_length=20, verbose_name="值")
    search_name = models.CharField(max_length=20, verbose_name="搜尋名稱")

    class Meta:
        verbose_name = "畜禽供應屠宰頭數"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.search_name}"


class LivestockByproduct(models.Model):
    parent = models.ForeignKey("LivestockByproduct", on_delete=models.CASCADE, null=True, blank=True, verbose_name="上層物件")
    main_class = models.CharField(max_length=50, verbose_name="主分類")
    sub_class = models.CharField(max_length=50, verbose_name="次分類")
    level = models.PositiveIntegerField(verbose_name="級別")
    name = models.CharField(max_length=20, verbose_name="名稱")
    value = models.CharField(max_length=20, verbose_name="值")
    search_name = models.CharField(max_length=20, verbose_name="搜尋名稱")

    class Meta:
        verbose_name = "畜禽副產品產量"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.search_name}"


class CropCost(models.Model):
    parent = models.ForeignKey("CropCost", on_delete=models.CASCADE, null=True, blank=True, verbose_name="上層物件")
    main_class = models.CharField(max_length=50, verbose_name="主分類")
    sub_class = models.CharField(max_length=50, verbose_name="次分類")
    level = models.PositiveIntegerField(verbose_name="級別")
    name = models.CharField(max_length=20, verbose_name="名稱")
    value = models.CharField(max_length=20, verbose_name="值")
    search_name = models.CharField(max_length=20, verbose_name="搜尋名稱")
    start_year = models.IntegerField(null=True, verbose_name="起始年")
    end_year = models.IntegerField(null=True, verbose_name="結束年")

    class Meta:
        verbose_name = "農畜產品生產成本統計"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.search_name}"


class ProductCode(models.Model):
    category = models.CharField(max_length=50, verbose_name="分類")
    code = models.CharField(max_length=50, verbose_name="代碼")
    name = models.CharField(max_length=50, verbose_name="名稱")

    class Meta:
        verbose_name = "作物代碼"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name}"


class CropPriceOrigin(models.Model):
    category = models.CharField(max_length=20, verbose_name="分類")
    id_table = models.CharField(max_length=20, verbose_name="表格ID")
    id_query = models.CharField(max_length=20, verbose_name="查詢ID")
    value = models.CharField(max_length=20, verbose_name="值")
    code = models.CharField(max_length=50, verbose_name="代碼")
    name = models.CharField(max_length=50, verbose_name="名稱")

    class Meta:
        verbose_name = "農耕作物產地價"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name}"


class CropPriceWholesale(models.Model):
    parent = models.ForeignKey("CropPriceWholesale", on_delete=models.CASCADE, null=True, blank=True, verbose_name="上層物件")
    main_class = models.CharField(max_length=50, verbose_name="主分類")
    sub_class = models.CharField(max_length=50, verbose_name="次分類")
    level = models.PositiveIntegerField(verbose_name="級別")
    name = models.CharField(max_length=20, verbose_name="名稱")
    value = models.CharField(max_length=20, verbose_name="值")
    search_name = models.CharField(max_length=20, verbose_name="搜尋名稱")

    class Meta:
        verbose_name = "農耕作物批發價"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name}"


class CropProduceUnit(models.Model):
    category = models.CharField(max_length=10, verbose_name="類別")
    display_name = models.CharField(max_length=50, verbose_name="顯示名稱")
    name = models.CharField(max_length=20, verbose_name="名稱")
    period = models.CharField(max_length=10, blank=True, null=True, verbose_name="期作別")
    city = models.CharField(max_length=20, verbose_name="城市")
    district = models.CharField(max_length=20, blank=True, null=True, verbose_name="鄉鎮區")
    city_district = models.CharField(max_length=20, blank=True, null=True, verbose_name="完整行政區名稱")
    city_code = models.CharField(max_length=20, verbose_name="城市代碼")
    district_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="鄉鎮區代碼")
    amount_min = models.FloatField(default=0, verbose_name="產量最小值")
    amount_max = models.FloatField(default=0, verbose_name="產量最大值")
    amount_average = models.FloatField(default=0, verbose_name="產量平均值")
    amount_unit = models.CharField(max_length=20, default="(公斤/公頃)", verbose_name="產量單位")
    value_min = models.FloatField(default=0, verbose_name="產值最大值")
    value_max = models.FloatField(default=0, verbose_name="產值最小值")
    value_average = models.FloatField(default=0, verbose_name="產值平均值")
    value_unit = models.CharField(max_length=20, default="(元/公頃)", verbose_name="產值單位")

    class Meta:
        verbose_name = "農耕作物產值產量表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.display_name}"


class CropProduceTotal(models.Model):
    name = models.CharField(max_length=20, verbose_name="名稱")
    value = models.CharField(max_length=10, verbose_name="值")

    class Meta:
        verbose_name = "作物產量作物清單"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name}"
