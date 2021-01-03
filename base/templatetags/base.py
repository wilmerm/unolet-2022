

from django import template
from django.conf import settings
from django.utils.translation import gettext as _

from unoletutils.libs import icons



register = template.Library()



@register.inclusion_tag("tags/icon.svg")
def svg(*args, **kwargs):
    """Muestra el contenido del ícono svg con el nombre indicado."""
    return icons.svg(*args, **kwargs)