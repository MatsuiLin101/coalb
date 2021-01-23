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


admin.site.register(ProduceValueCity, ProduceValueCityAdmin)
admin.site.register(ProduceValueFarmCategory)
admin.site.register(ProduceValueProduct, ProduceValueProductAdmin)
