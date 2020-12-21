from django.contrib import admin

from .models import LineUser, SD


class LineUserAdmin(admin.ModelAdmin):
    list_display = [
        'user_id', 'display_name', 'status', 'created', 'updated'
    ]


admin.site.register(LineUser, LineUserAdmin)
admin.site.register(SD)
