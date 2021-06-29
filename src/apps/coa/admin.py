from django.contrib import admin

from apps.coa.models import *


class ProduceValueCityAdmin(admin.ModelAdmin):
    list_display = [
        "id", "name", "value", "province", "type"
    ]
    list_filter = [
        "type"
    ]


class ProduceValueProductAdmin(admin.ModelAdmin):
    list_display = [
        "id", "name", "value", "category", "city_type"
    ]
    list_filter = [
        "category", "city_type"
    ]
    search_fields = [
        "name"
    ]


class LivestockFeedlotAdmin(admin.ModelAdmin):
    list_display = [
        "parent", "search_name", "level", "name", "main_class", "sub_class"
    ]


class LivestockFeedamountAdmin(admin.ModelAdmin):
    list_display = [
        "parent", "search_name", "level", "name", "main_class", "sub_class"
    ]


class LivestockSlaughterAdmin(admin.ModelAdmin):
    list_display = [
        "parent", "search_name", "level", "name", "main_class", "sub_class"
    ]


class LivestockByproductAdmin(admin.ModelAdmin):
    list_display = [
        "parent", "search_name", "level", "name", "main_class", "sub_class"
    ]


admin.site.register(ProduceValueCity, ProduceValueCityAdmin)
admin.site.register(ProduceValueFarmCategory)
admin.site.register(ProduceValueProduct, ProduceValueProductAdmin)
admin.site.register(LivestockFeedlot, LivestockFeedlotAdmin)
admin.site.register(LivestockFeedamount, LivestockFeedamountAdmin)
admin.site.register(LivestockSlaughter, LivestockSlaughterAdmin)
admin.site.register(LivestockByproduct, LivestockByproductAdmin)
