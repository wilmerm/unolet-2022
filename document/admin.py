from django.contrib import admin

from .models import (DocumentType, Document)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    readonly_fields = ("amount", "discount", "tax", "total")


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    pass