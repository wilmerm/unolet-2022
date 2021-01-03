"""
base.context_processors.base

Procesador de contexto del proyecto.
"""

from django.conf import settings
from django.utils.translation import gettext_lazy as _l
from django.urls import reverse_lazy, reverse
from django.apps import apps

from unoletutils.libs import icons, var


VAR = vars(var)


class Model:

    def __init__(self, model, app_label, request):
        self.model = model
        self.app_label = app_label
        self.request = request
    
    def __getitem__(self, name):
        return getattr(self.model, name, getattr(self.model._meta, name))

    def get_index_url(self):
        return reverse(f"{self.app_label}-{self.model._meta.model_name}-index".lower(), kwargs={"company": self.request.company.pk})

    def get_list_url(self):
        return reverse(f"{self.app_label}-{self.model._meta.model_name}-list".lower(), kwargs={"company": self.request.company.pk})

    def get_url(self):
        try:
            return self.get_index_url()
        except (BaseException) as e1:
            try:
                return self.get_list_url()
            except (BaseException) as e2:
                raise ValueError(f"{e1}, \n{e2}")



class App:

    def __init__(self, request, label, name, description, icon, url):
        self.request = request
        self.label = label
        self.name = _l(name)
        self.description = _l(description)
        self.url = url
                
        self.icon = icons.svg(icon).get("svg") or icon
        self.icon_name = icon
        self.app_config = apps.get_app_config(self.label)
        self.models = [Model(model, label, request) for model in self.app_config.get_models()]

    def __str__(self):
        return str(self.name)




def base(request):
    return {
        "settings": settings,
        "title": "",

        "apps": [
            App(request, "warehouse", "Almacenes", "Gestión de almacenes", "house-fill", ""),
            #App(request, "user", "Usuarios", "Gestión de usuarios", "person-circle", ""),
        ],

        "var": VAR,
    }

