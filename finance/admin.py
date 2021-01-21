from django.contrib import admin

from .models import (Currency, Transaction)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    readonly_fields = ("is_default",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    pass