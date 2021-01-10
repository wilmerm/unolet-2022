from django import template
from django.conf import settings
from django.utils.html import format_html
from django.utils.translation import gettext as _
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
    if value is True:
        return format_html('<span class="text-success font-weight-bold">{}<span>', "✅")
    if value is False:
        return format_html('<span class="text-danger">{}<span>', "⛔")
    if value in (None, ""):
        return ""
    if isinstance(value, dict):
        return dict_to_ul(value)
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
    return {"request": request}


@register.inclusion_tag("tags/modules.html")
def modules(request):
    parent = Module.get_from_request(request)
    module_list = request.user.get_modules(parent=parent)
    return {"request": request, "module_list": module_list}


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
            action_links = obj.get_actions_links(defaults=defaults.split(), size=size)
        except (AttributeError):
            action_links = {}
    return {"action_links": action_links, "obj": obj, "size": size}


@register.inclusion_tag("tags/detail_field.html")
def detail_field(request=None, name="", value="", url=""):
    return {"request": request, "name": name, "value": value, "url": url}


@register.inclusion_tag("tags/create_button.html")
def create_button(request, obj=None, model=None, size="1rem"):
    url_name_list = request.resolver_match.url_name.split("-")
    if not url_name_list:
        return {}
    if url_name_list[-1] in ["create", "detail", "update", "delete", "list", "index"]:
        url_name = "-".join(url_name_list[:-1] + ["create"])

    company = request.company

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