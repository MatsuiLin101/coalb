from django.contrib import admin

from apps.coa.models import *


class DynamicSearchAdmin(admin.ModelAdmin):
    list_display = [
        "parent", "search_name", "level", "name", "main_class", "sub_class"
    ]
    list_filter = [
        "sub_class"
    ]
    search_fields = [
        "name", "main_class", "sub_class"
    ]


class CropCostAdmin(DynamicSearchAdmin):
    list_display = [
        "parent", "search_name", "level", "name", "main_class", "sub_class", "start_year", "end_year"
    ]
    search_fields = [
        "name"
    ]


class ProductCodeAdmin(admin.ModelAdmin):
    list_display = [
        "category", "code", "name"
    ]
    search_fields = [
        "category", "code", "name"
    ]


class CropPriceOriginAdmin(admin.ModelAdmin):
    list_display = [
        "category", "name"
    ]
    search_fields = [
        "category", "name"
    ]


class CropProduceUnitAdmin(admin.ModelAdmin):
    list_display = [
        "name", "city_district", "amount_average", "value_average"
    ]
    list_filter = [
        "category", "city",
    ]
    search_fields = [
        "name", "city_district"
    ]


class CropProduceTotalAdmin(admin.ModelAdmin):
    list_display = [
        "name", "value"
    ]
    search_fields = [
        "name", "value"
    ]


admin.site.register(TotalValue, DynamicSearchAdmin)
admin.site.register(LivestockFeedlot, DynamicSearchAdmin)
admin.site.register(LivestockFeedamount, DynamicSearchAdmin)
admin.site.register(LivestockSlaughter, DynamicSearchAdmin)
admin.site.register(LivestockByproduct, DynamicSearchAdmin)
admin.site.register(CropCost, CropCostAdmin)
admin.site.register(ProductCode, ProductCodeAdmin)
admin.site.register(CropPriceOrigin, CropPriceOriginAdmin)
admin.site.register(CropPriceWholesale, DynamicSearchAdmin)
admin.site.register(CropProduceUnit, CropProduceUnitAdmin)
admin.site.register(CropProduceTotal, CropProduceTotalAdmin)
