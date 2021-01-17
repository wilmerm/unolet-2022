from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext as _
from django.views import generic
from django.http import JsonResponse

from unoletutils.libs import text
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
    

# Json views.

def item_list_jsonview(request, company: int) -> JsonResponse:
    """Obtiene un listado de artículos filtrados por el parámetro 'q' en URL."""

    qs = Item.active_objects.all()

    if request.GET.get("q"):
        qs = qs.filter(tags__icontains=text.Text.get_tag(request.GET["q"]))

    item_list = list(qs.values(
        "id", "code", "codename", "name", "description", 
        "group_id", "group__name",
        "family_id", "family__name",
        "tax_id", "tax__name", "tax__value", "tax__value_type",
        "min_price", "max_price", "available",
        "is_active"
    ))

    return JsonResponse({"data": {"items": item_list, "count": qs.count()}})


