from django.contrib import admin

# Register your models here.
from . models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user','image')
    search_fields = ('user','bio')

admin.site.register(UserProfile, UserProfileAdmin)    
    