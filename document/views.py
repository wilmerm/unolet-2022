from django.shortcuts import render
from django.views.generic import (DetailView, UpdateView, CreateView, ListView)

from unoletutils.libs.utils import view_decorator
from .models import (Document, DocumentType)
from .forms import (DocumentForm)


@view_decorator(company_field="doctype__company")
class DocumentUpdateView(UpdateView):
    """Modifica un documento."""
    model = Document
    form_class = DocumentForm
