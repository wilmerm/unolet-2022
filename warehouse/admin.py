from django.contrib import admin
from .models import Warehouse



@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):

    list_display = ["site", "company", "name", "is_active"]
    
    search_fields = ["company__name", "name"]

    list_filter = ["company__site", "company", "is_active"]

    def site(self, obj):
        return obj.company.site