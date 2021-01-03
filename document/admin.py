from django.contrib import admin

from .models import (DocumentType, Document)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    pass 


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    pass