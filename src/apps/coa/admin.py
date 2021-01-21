from django.contrib import admin

from apps.coa.models import *


class ProduceValueCityAdmin(admin.ModelAdmin):
    list_display = [
        "id", "name", "value", "province"
    ]


admin.site.register(ProduceValueCity, ProduceValueCityAdmin)
admin.site.register(ProduceValueFarmCategory)
