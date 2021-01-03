from django.contrib import admin

from .models import (Currency)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    readonly_fields = ("is_default",)