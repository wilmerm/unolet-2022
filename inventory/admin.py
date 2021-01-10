from django.contrib import admin
from .models import (Item, ItemFamily, ItemGroup, Movement)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    pass #readonly_fields = ("company", "code")


@admin.register(ItemFamily)
class ItemFamilyAdmin(admin.ModelAdmin):
    pass #readonly_fields = ("company",)


@admin.register(ItemGroup)
class ItemGroupAdmin(admin.ModelAdmin):
    pass #readonly_fields = ("company",)


@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    pass



