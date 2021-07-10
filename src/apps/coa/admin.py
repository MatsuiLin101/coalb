from django.contrib import admin

from apps.coa.models import *


class DynamicSearchAdmin(admin.ModelAdmin):
    list_display = [
        "parent", "search_name", "level", "name", "main_class", "sub_class"
    ]
    list_filter = [
        "sub_class"
    ]


class ProductCodeAdmin(admin.ModelAdmin):
    list_display = [
        "category", "code", "name"
    ]


class CropPriceOriginAdmin(admin.ModelAdmin):
    list_display = [
        "category", "name"
    ]


class CropProduceUnitAdmin(admin.ModelAdmin):
    list_display = [
        "name", "city_district", "amount_average", "value_average"
    ]
    list_filter = [
        "category", "city",
    ]


admin.site.register(TotalValue, DynamicSearchAdmin)
admin.site.register(LivestockFeedlot, DynamicSearchAdmin)
admin.site.register(LivestockFeedamount, DynamicSearchAdmin)
admin.site.register(LivestockSlaughter, DynamicSearchAdmin)
admin.site.register(LivestockByproduct, DynamicSearchAdmin)
admin.site.register(CropCost, DynamicSearchAdmin)
admin.site.register(ProductCode, ProductCodeAdmin)
admin.site.register(CropPriceOrigin, CropPriceOriginAdmin)
admin.site.register(CropPriceWholesale, DynamicSearchAdmin)
admin.site.register(CropProduceUnit, CropProduceUnitAdmin)
admin.site.register(CropProduceTotal)
