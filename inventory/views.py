from django.shortcuts import render
from django.views.generic import (DetailView, CreateView, UpdateView, ListView)

from unoletutils.libs.utils import view_decorator
from .models import (Item, ItemFamily, ItemGroup, Movement)
from .forms import (ItemForm)


@view_decorator()
class ItemCreateView(CreateView):
    """Vista para la creaciónd e artículos."""
    model = Item
    form_class = ItemForm


@view_decorator()
class ItemUpdateView(UpdateView):
    """Vista para la modificación de artículos."""
    model = Item
    form_class = ItemForm
    