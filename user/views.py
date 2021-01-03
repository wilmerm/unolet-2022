from django.shortcuts import render
from django.views.generic import (TemplateView, DetailView, UpdateView, 
    CreateView, DeleteView, ListView)
from django.contrib.auth.mixins import (LoginRequiredMixin, 
    PermissionRequiredMixin)

from .models import User



class IndexView(LoginRequiredMixin, TemplateView):
    """Página principal del módulo usuarios."""

    template_name = "user/index.html"


class UserListView(PermissionRequiredMixin, ListView):
    """Listado de usuarios."""

    model = User

