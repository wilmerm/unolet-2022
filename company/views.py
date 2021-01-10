from django.shortcuts import render, get_object_or_404
from django.views.generic import (DetailView, UpdateView)
from django.contrib.auth.mixins import (LoginRequiredMixin, 
    PermissionRequiredMixin)

from .models import Company


class CompanyDetailView(LoginRequiredMixin, DetailView):
    """Detalle de una empresa."""

    model = Company

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs.get("company"))


