from django.contrib import admin
from .models import Company, CompanyPermission, CompanyPermissionGroup


@admin.register(Company)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ["site", "name", "is_active"]
    search_fields = ["site", "name"]
    list_filter = ["site", "is_active"]

    def site(self, obj):
        return obj.company.site


@admin.register(CompanyPermission)
class CompanyPermissionAdmin(admin.ModelAdmin):
    readonly_fields = ("codename",)


@admin.register(CompanyPermissionGroup)
class CompanyPermissionGroupAdmin(admin.ModelAdmin):
    pass