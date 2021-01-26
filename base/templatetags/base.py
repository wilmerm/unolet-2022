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


@register.simple_tag
def get_attr(obj, name, default=""):
    """return getattr(obj, name)."""
    return getattr(obj, name, default)


@register.filter
def to_html(value):
    """"""
    if (value is True) or (value in ("True", "true")):
        return format_html('<span class="text-success font-weight-bold">{}<span>', "✅")
    if (value is False) or (value in ("False", "false")):
        return format_html('<span class="text-danger">{}<span>', "⛔")
    if value in (None, ""):
        return ""
    if value == "+":
        return format_html(icons.svg("plus-circle-fill", fill="var(--success)")["svg"])
    if value == "~":
        return format_html(icons.svg("pencil-fill", fill="var(--warning)")["svg"])
    if value == "-":
        return format_html(icons.svg("dash-circle-fill", fill="var(--danger)")["svg"])
    if isinstance(value, dict):
        return dict_to_ul(value)
    return readable(value)


@register.filter
def readable(value):
    """Convierte el valor a un texto que sea leíble para un humano."""
    if (value is True) or (value in ("True", "true")):
        return _("si")
    if (value is False) or (value in ("False", "false")):
        return _("no")
    if (value is None) or (value in ("None", "none", "null")):
        return _("ninguno")
    if value == "":
        return ""
    if value == "+":
        return _("creó")
    if value == "~":
        return _("modificó")
    if value == "-":
        return _("eliminó")
    return value


@register.filter
def verbose_name_plural(obj):
    """Trata de encontrar el verbose_name_plural atributo del obj."""
    try:
        return obj.model._meta.verbose_name_plural
    except (AttributeError):
        try:
            return obj.__class__._meta.verbose_name_plural
        except (AttributeError):
            try:
                return obj._meta.verbose_name_plural
            except (AttributeError):
                pass
    return ""


@register.simple_tag
def vue(value: str) -> str:
    """Encierra el valor en doble llaves 'value' -> '{{ value }}'."""
    return "{{ %s }}" % value


@register.filter
def vue(value: str) -> str:
    """Encierra el valor en doble llaves 'value' -> '{{ value }}'."""
    return "{{ %s }}" % value


@register.inclusion_tag("tags/history.html")
def history(obj, title=_l("Historial de cambios"), extra_classes=""):
    """Muestra el historial de cambios del objeto indicado."""
    return {"object": obj, "title": title, "extra_classes": extra_classes}

    
@register.inclusion_tag("tags/icon.svg")
def svg(*args, **kwargs):
    """Muestra el contenido del ícono svg con el nombre indicado."""
    return icons.svg(*args, **kwargs)


@register.inclusion_tag("tags/pagination.html")
def pagination(page_obj, request, **kwargs):
    kwargs["size"] = kwargs.get("size", "small")
    kwargs.update({"page_obj": page_obj, "request": request})
    return kwargs


@register.inclusion_tag("tags/menu.html")
def menu(request):
    """Muestra los módulos de la URL actual a los que el usuario puede tener
    acceso, en un estilo de menú."""
    return {"request": request}


@register.inclusion_tag("tags/modules.html")
def modules(request):
    """Muestra los módulos de la URL actual a los que el usuario puede tener 
    acceso."""
    parent = Module.get_from_request(request)
    module_list = request.user.get_modules(parent=parent)
    return {"request": request, "module": parent, "module_list": module_list}


@register.inclusion_tag("tags/breadcrumb.html")
def breadcrumb(request, limit=20):
    """Muestra el link de módulos desde el actual obteniendo los padres."""
    links = []
    current = Module.get_from_request(request)

    if current is None:
        return {"links": links}

    links.append({
        "name": str(current),
        "url": "",
        "img": current.get_img(),
        "cssclass": "active",
    })

    for n in range(limit):
        current = current.parent
        if current is None:
            break

        links.append({
            "name": str(current),
            "url": current.get_absolute_url(request.company),
            "img": current.get_img(),
            "cssclass": "",
        })
    links.reverse()
    return {"links": links}


@register.inclusion_tag("tags/dict_to_ul.html")
def dict_to_ul(dic):
    """Muestra un object dict como una lista HTML ul tag."""
    if not dic:
        return {"ul": ""}
    dic_obj = dict()
    li_list = []
    exclude_keys = ["form"]
    for key, value in dic.items():

        if isinstance(value, dict):
            ul = dict_to_ul(value)["ul"]
            li = f"<li><b>{key}: </b>{ul}</li>"
        elif isinstance(value, (list, tuple)):
            value = {i: value[i] for i in range(len(value[:20]))}
            ul = dict_to_ul(value)["ul"]
            li = f"<li><b>{key}: </b>{ul}</li>"
        elif isinstance(value, models.QuerySet):
            value = {e.id: str(e) for e in value[:20]}
            ul = dict_to_ul(value)["ul"]
            li = f"<li><b>{key}: </b>{ul}</li>"
        elif (not str(key).startswith("_")) and (not key in exclude_keys):
            li = f"<li><b>{key}: </b>{value}</li>"
        else:
            continue
        
        li_list.append(li)
    ul = f"<ul>%s</ul>" % "".join(li_list)
    return {"ul": ul}


@register.inclusion_tag("tags/list_action_links_for_object.html")
def list_action_links_for_object(*objs, defaults="detail update delete", **options):
    """
    Muestra las acciones disponibles para el primer objeto del listado que 
    contenga el método get_actions_links.
    """
    size = options.get("size", "1rem")
    for obj in objs:
        try:
            action_links = obj.get_actions_links(
                defaults=defaults.split(), size=size)
        except (AttributeError):
            action_links = {}
    return {"action_links": action_links, "obj": obj, "size": size}


@register.inclusion_tag("tags/detail_field.html")
def detail_field(request=None, name="", value="", url=None, img=None):
    if url is None:
        try:
            url = str(value.get_absolute_url())
        except (AttributeError, NoReverseMatch):
            url = ""
    img = img or getattr(value, "get_img", "")
    return {"request": request, "name": name, "value": value, "url": url, 
        "img": img}


@register.inclusion_tag("tags/create_button.html")
def create_button(request, obj=None, model=None, size="1rem", url=None):

    company = request.company

    if url == None:
        url_name_list = request.resolver_match.url_name.split("-")

        if not url_name_list:
            return {}

        if url_name_list[-1] in ["create", "detail", "update", "delete", "list", "index"]:
            url_name = "-".join(url_name_list[:-1] + ["create"])

        try:
            url = reverse(url_name, kwargs={"company": company.pk})
        except (NoReverseMatch):
            return {}
    
    return {"url": url, "size": size, "request": request, "company": company}


@register.inclusion_tag("tags/developer_data.html")
def developer_data(view, request):
    """Muestra información adicional para el equipo de desarrolladores."""
    user = request.user
    if not user.is_superuser:
        return {}
    out = dict(
        view_dict = view.__dict__,
        view_class_dict = view.__class__.__dict__,
        view_doc = view.__doc__,
        context_dict = view.get_context_data(),
        request_dict = request.__dict__,
        user_company_permissions = user.get_company_permissions(request.company),
        user_company_groups = user.get_company_groups(request.company),
        user = user,
    )
    if hasattr(view.__class__, "model"):
        out["app_label"] = view.__class__.model._meta.app_label
        out["model_name"] = view.__class__.model._meta.model_name
        out["model_doc"] = view.__class__.model.__doc__
    
    return out