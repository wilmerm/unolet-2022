
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext as _
from django.views import generic
from django.http import JsonResponse, Http404

from unoletutils.libs import text
from unoletutils.views import (ListView, DetailView, UpdateView, CreateView, 
    DeleteView, TemplateView, JsonResponseMixin)
from company.models import Company
from document.models import Document
from inventory.models import (Item, ItemFamily, ItemGroup, Movement)
from inventory.forms import (ItemGroupForm, ItemFamilyForm, ItemForm, MovementForm)


class Index(TemplateView):
    """Página principal de la app inventario."""
    template_name = "inventory/index.html"


class ItemGroupCreateView(CreateView):
    """Vista para la creación de grupos de artículos."""
    model = ItemGroup
    form_class = ItemGroupForm


class ItemGroupDetailView(DetailView):
    """Vista que muestra el detalle de un grupo de artículo."""
    model = ItemGroup


class ItemGroupUpdateView(UpdateView):
    """Vista para la modificación de groupos artículos."""
    model = ItemGroup
    form_class = ItemGroupForm
    

class ItemGroupListView(ListView):
    """Listado de grupos de artículos."""
    model = ItemGroup
    

class ItemFamilyCreateView(CreateView):
    """Vista para la creación de familias de artículos."""
    model = ItemFamily
    form_class = ItemFamilyForm


class ItemFamilyDetailView(DetailView):
    """Vista que muestra el detalle de un familia de artículo."""
    model = ItemFamily


class ItemFamilyUpdateView(UpdateView):
    """Vista para la modificación de familias artículos."""
    model = ItemFamily
    form_class = ItemFamilyForm
    

class ItemFamilyListView(ListView):
    """Listado de familias de artículos."""
    model = ItemFamily
    

class ItemCreateView(CreateView):
    """Vista para la creación de artículos."""
    model = Item
    form_class = ItemForm


class ItemDetailView(DetailView):
    """Vista que muestra el detalle de un artículo."""
    model = Item


class ItemUpdateView(UpdateView):
    """Vista para la modificación de artículos."""
    model = Item
    form_class = ItemForm
    

class ItemListView(ListView):
    """Listado de artículos."""
    model = Item
    list_display = (
        ("codename", _("Referencia")),
        ("code", _("Código")),
        ("name", _("Nombre")),
        ("description", _("Descripción")),
        ("group", _("Grupo")),
        ("family", _("Familia")),
        ("get_available", _("Disponible")),
    )

    list_display_cssclass = {
        "get_available": "text-end",
    }


class ItemMovementListView(ListView):
    """Listado de movimientos de un artículo específico."""
    model = Movement
    template_name = "inventory/item_movement_list.html"

    def get_title(self):
        return "%s %s" % (_("Movimientos del articulo"), self.item)

    def dispatch(self, request, *args, **kwargs):
        self.item = get_object_or_404(Item, pk=kwargs.pop("item"))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.item.movement_set.all()


class MovementListView(ListView):
    """Listado de movimienetos."""
    model = Movement
    template_name = "inventory/movement_list.html"


class MovementDetailView(DetailView):
    """Detalle de un movimiento."""
    model = Movement
    template_name = "inventory/movement_detail.html"


# Json views.

def item_list_jsonview(request, company: int) -> JsonResponse:
    """Obtiene un listado de artículos filtrados por el parámetro 'q' en URL."""

    try:
        limit = int(request.GET.get("limit"))
    except (TypeError, ValueError):
        limit = 20
    
    qs = Item.active_objects.filter(company=company)

    if request.GET.get("q"):
        qs = qs.filter(tags__icontains=text.Text.get_tag(request.GET["q"]))
    else:
        qs = qs.none()

    qs = qs[:limit]
    item_list = list(qs.values(
        "id", "code", "codename", "name", "description", 
        "group_id", "group__name",
        "family_id", "family__name",
        "tax_id", "tax__name", "tax__value", "tax__value_type",
        "min_price", "max_price", "available",
        "is_active"
    ))
    return JsonResponse({"data": {"items": item_list, "count": qs.count()}})


def json_response_error(field: str, message: str, code: str="", status=404):
    error = {field: [{"message": message, "code": code}]}
    return JsonResponse({"errors": error}, status=status)


def movement_form_jsonview(request, company: int, document: int) -> JsonResponse:
    """Crea o modifica un movimiento y devuelve un JsonResponse."""
    company = get_object_or_404(Company, pk=company)
    document = get_object_or_404(Document, doctype__company=company, pk=document)

    # El usuario deberá tener alguno de estos dos permisos. Más adelante 
    # volveremos a comprobar los permisos según sea una edición o creación.
    if not request.user.has_company_permission(company, 
        ("inventory.add_movement", "inventory.change_movement")):
        return json_response_error("global", _("Permiso denegado."))

    if request.method == "POST":
        try:
            document_pk = int(request.POST["document"])
        except (KeyError, ValueError, TypeError) as e:
            return json_response_error("global", _("El documento es requerido"), 
                "required", 400)

        if document_pk != document.pk:
            return json_response_error("global", _("No válido"))

        # El item según el modelo puede ser nulo, pero aquí queremos un item.
        try:
            item = Item.objects.get(pk=int(request.POST["item"]), company=company)
        except (KeyError, ValueError, TypeError, Item.DoesNotExist) as e:
            return json_response_error("item", _("El artículo es requerido"), 
                "required", 400)

        try:
            pk = int(request.POST["id"])
        except (KeyError, ValueError, TypeError):
            # El usuario deberá tener el permiso de crear movimientos.
            if not request.user.has_company_permission(
                company, "inventory.add_movement"):
                return json_response_error("global", _("Permiso denegado."))
            pk = None
            form = MovementForm(request.POST, company=company)
        else:
            # El usuario deberá tener el permiso de modificar movimientos.
            if not request.user.has_company_permission(
                company, "inventory.change_movement"):
                return json_response_error("global", _("Permiso denegado."))
                
            instance = Movement.objects.get(pk=pk, document=document)
            form = MovementForm(request.POST, company=company, instance=instance)

        if form.is_valid():
            instance = form.save(commit=False)
            # Lógica. ....
            instance.save()
            return JsonResponse({"data": {"pk": instance.pk}})
        else:
            errors = form.errors.as_json()
            print(errors)
            return JsonResponse({"errors": errors}, status=400)
    else:
        form = MovementForm(company=company)
    return JsonResponse({"data": {"company": company.pk, "document": document}})

    
def movement_delete_jsonview(request, company, document) -> JsonResponse:
    """Elimina un movimiento y retorna un JsonResponse."""
    # Realizamos una consulta compleja para asegurarnos que la 
    # solicitud sea válida, realizada desde la misma empresa y 
    # documento al que pertenece el movimiento.
    movement = get_object_or_404(Movement, document__doctype__company=company, 
        document=document, pk=request.POST.get("id"))

    movement.delete()
    return JsonResponse({"id": request.POST.get("id"), "delete": True})
    



class MovementCreateView(JsonResponseMixin, CreateView):
    """Crea un movimiento."""

    model = Movement
    form_class = MovementForm

