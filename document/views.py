from django.shortcuts import render
from django.views.generic import (DetailView, UpdateView, CreateView, ListView)

from unoletutils.views import (UpdateView, CreateView, ListView, DetailView, 
    DeleteView, TemplateView)
from .models import (Document, DocumentType)
from .forms import (DocumentForm)


class DocumentUpdateView(UpdateView):
    """Modifica un documento."""
    model = Document
    form_class = DocumentForm
    company_field = "doctype__company"


class DocumentCreateView(CreateView):
    """Crea un documento."""
    model = Document
    form_class = DocumentForm