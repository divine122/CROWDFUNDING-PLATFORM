from django.contrib import admin

from .models import Logbook

@admin.register(Logbook)
class LogbookAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp', 'description')  

