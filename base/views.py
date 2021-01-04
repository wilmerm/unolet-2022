from django.shortcuts import render
from django.views.generic import (TemplateView)
from django.contrib.auth.mixins import (LoginRequiredMixin, 
    PermissionRequiredMixin)


def handler400(request, exception=None):
    response = render(request, "error/400.html", {})
    response.status_code = 400
    return response


def handler403(request, exception=None):
    response = render(request, "error/403.html", {})
    response.status_code = 403
    return response


def handler404(request, exception=None):
    response = render(request, "error/404.html", {})
    response.status_code = 404
    return response


def handler500(request, exception=None):
    response = render(request, "error/500.html", {})
    response.status_code = 500
    return response


class IndexView(LoginRequiredMixin, TemplateView):
    """Página principal."""

    template_name = "base/index.html"


