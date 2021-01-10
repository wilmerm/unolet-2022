from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views import generic

from unoletutils.views import (ListView, DetailView, UpdateView, CreateView, 
    DeleteView, TemplateView)
from .models import (Item, ItemFamily, ItemGroup, Movement)
from .forms import (ItemForm)


class Index(TemplateView):
    """Página principal de la app inventario."""
    template_name = "inventory/index.html"


class ItemCreateView(CreateView):
    """Vista para la creación e artículos."""
    model = Item
    form_class = ItemForm


class ItemUpdateView(UpdateView):
    """Vista para la modificación de artículos."""
    model = Item
    form_class = ItemForm
    

class ItemListView(ListView):
    """Listado de artículos."""
    model = Item
    list_display = (
        ("codename", _("Referencia")),
        ("code", _("Código")),
        ("name", _("Nombre")),
        ("description", _("Descripción")),
        ("group", _("Grupo")),
        ("family", _("Familia")),
        ("get_available", _("Disponible")),
    )

    list_display_cssclass = {
        "get_available": "text-end",
    }
    
