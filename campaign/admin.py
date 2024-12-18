from django.contrib import admin

# Register your models here.
from . models import Campaign,CampaignPage,Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

  


admin.site.register(CampaignPage)

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'goal_amount', 'description','category_type')

# You can create custom actions to allow admins to approve, reject, or flag projects directly from the admin panel.

    def approve_campaigns(self, request, queryset):
        queryset.update(approval_status='approved')
        self.message_user(request, "Selected campaigns have been approved.")

    def reject_campaigns(self, request, queryset):
        queryset.update(approval_status='rejected')
        self.message_user(request, "Selected campaigns have been rejected.")

    def flag_campaigns(self, request, queryset):
        queryset.update(flagged=True)
        self.message_user(request, "Selected campaigns have been flagged as inappropriate.")


    def mark_as_active(self, request, queryset):
        queryset.update(status=Campaign.ACTIVE)
        self.message_user(request, "Selected campaigns are now active.")

    def mark_as_successful(self, request, queryset):
        queryset.update(status=Campaign.COMPLETED)
        self.message_user(request, "Selected campaigns are now completed.")

    def mark_as_failed(self, request, queryset):
        queryset.update(status=Campaign.FAILED)
        self.message_user(request, "Selected campaigns are now failed.")

    def mark_as_draft(self,request,queryset):
        queryset.update(status=Campaign.DRAFT)
        self.message_user(request, "Selected campaigns are draft")       


    

