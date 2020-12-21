from django.contrib import admin

from . import models


class LineBodyLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'body', 'created'
    ]


admin.site.register(models.LineBodyLog, LineBodyLogAdmin)
