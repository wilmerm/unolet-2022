from django.shortcuts import render
from django.views.generic import (TemplateView)



class IndexView(TemplateView):
    """Página principal."""

    template_name = "base/index.html"


