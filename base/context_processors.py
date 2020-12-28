"""
base.context_processors.base

Procesador de contexto del proyecto.
"""

from django.conf import settings



def base(request):
    return {
        "settings": settings,
        "title": "",
    }