from django.contrib import admin

from apps.coa.models import *


class ProduceValueCityAdmin(admin.ModelAdmin):
    list_display = [
        "id", "name", "value", "province"
    ]


class ProduceValueProductAdmin(admin.ModelAdmin):
    list_display = [
        "id", "name", "value", "category"
    ]
    list_filter = [
        "category"
    ]
    search_fields = [
        "name"
    ]


admin.site.register(ProduceValueCity, ProduceValueCityAdmin)
admin.site.register(ProduceValueFarmCategory)
admin.site.register(ProduceValueProduct, ProduceValueProductAdmin)
