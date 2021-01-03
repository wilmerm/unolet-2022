from django import forms

from base.forms import ModelForm
from .models import (Document, DocumentType)


class DocumentForm(ModelForm):
    """Formulario para documentos."""

    class Meta:
        model = Document
        fields = "__all__"
