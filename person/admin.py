from django.contrib import admin

from person.models import (Person, IdentificationType)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("identification", "name", "business_name")


@admin.register(IdentificationType)
class IdentificationTypeAdmin(admin.ModelAdmin):
    list_display = ("name", )