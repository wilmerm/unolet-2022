from django.contrib import admin

from module.models import Module


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    """Module."""
    