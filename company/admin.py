from django.contrib import admin
from .models import Company



@admin.register(Company)
class WarehouseAdmin(admin.ModelAdmin):

    list_display = ["site", "name", "is_active"]
    
    search_fields = ["site", "name"]

    list_filter = ["site", "is_active"]

    def site(self, obj):
        return obj.company.site