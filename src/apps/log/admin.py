from django.contrib import admin

from . import models


class LineBodyLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'body', 'created'
    ]


class LineMessageLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'message', 'status', 'created'
    ]


class LineFollowLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'message', 'status', 'created'
    ]


admin.site.register(models.LineBodyLog, LineBodyLogAdmin)
admin.site.register(models.LineMessageLog, LineMessageLogAdmin)
admin.site.register(models.LineFollowLog, LineFollowLogAdmin)
