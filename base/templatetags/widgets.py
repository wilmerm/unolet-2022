"""
Elementos predefinidos para ser utilizados en plantillas.
"""

from django import template
from django.conf import settings
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l
from django.db import models
from django.urls import reverse, NoReverseMatch

from unoletutils.libs import icons

from module.models import Module


register = template.Library()


@register.inclusion_tag("tags/widgets/btn_print.html")
def btn_print(tag="a", Type="button", title="Imprimir", cssclass="btn btn-info",
    icon_name="printer-fill"):
    pass