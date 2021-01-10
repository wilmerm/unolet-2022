import copy
import functools

from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l
from django.views import generic


class ViewError(Exception):
    pass



class ObjectCapsule:
    """
    Encapsula una instancia de un models.Model para poder llamar a métodos 
    declarados en la vista mediante el atributo de clase 'list_display'.
    """

    def __init__(self, view, obj):
        self._view = view

        if isinstance(obj, ObjectCapsule):
            obj = obj._obj
        self._obj = obj 

    def __str__(self):
        return str(self._obj)

    def __bool__(self):
        return bool(self._obj)

    def __getattribute__(self, name):
        try:
            return getattr(super().__getattribute__("_view"), name)
        except (AttributeError) as e2:
            pass
        try:
            return getattr(super().__getattribute__("_obj"), name)
        except (AttributeError) as e1:
            pass
        try:
            return super().__getattribute__(name)
        except (AttributeError) as e3:
            pass

        raise AttributeError(e1, e2, e3) from e1

    def get_values(self):
        """Obtiene los valores de los campos declarados en list_display. """
        return {
            e[0]: {"value": getattr(self, e[0]), 
                "cssclass": self.get_list_display_cssclass().get(e[0])} 
            for e in self._view.get_list_display()}


class QuerysetCapsule:
    """
    Encapsula un objeto Queryset para poder recorrer cada uno de sus elementos 
    de forma encapsulada con ObjectCapsule.
    """

    def __init__(self, view, queryset):
        self._view = view 
        self._queryset = queryset 

    def __iter__(self):
        for obj in self._queryset:
            yield ObjectCapsule(self._view, obj)

    def __len__(self):
        return len(self._queryset)

    def __getitem__(self, index):
        if isinstance(index, int):
            return ObjectCapsule(self._view, self._queryset[index])
        return QuerysetCapsule(self._view, self._queryset[index])

    def __getattribute__(self, name):
        if name in ("_view", "_queryset", "__iter__"):
            return object.__getattribute__(self, name)

        return getattr(self._queryset, name)


class BaseView:
    """Clase base de las cuales heredarán nuestras vistas."""

    company_field = "company"
    company_in_url = "company"
    pk_field = "pk"
    pk_in_url = "pk"
    error_list = []
    company_permission_required = None

    def get_company(self):
        """Obtiene la instancia de la empresa actual."""
        try:
            company = self.request.company
        except (AttributeError):
            try:
                company = self.get_context_data()["company"]
            except (AttributeError, KeyError):
                company = get_object_or_404(Company, pk=kwargs[self.company_in_url])
        return company

    def get_object(self, queryset=None):
        company = self.get_company()
        company_pk = self.kwargs.get(self.company_in_url)
        pk = self.kwargs.get(self.pk_in_url)
        
        if company_pk and pk:
            filters = {self.company_field: company_pk, self.pk_field: pk}
            obj = get_object_or_404(self.model, **filters)
        else:
            obj = None
            
        # La objeto debe pertenecer a la misma empresa obtenida por url.
        if obj:
            #obj_company = functools.reduce(getattr, [obj] + self.company_field.split("__"))
            obj_company = obj.getattr(self.company_field)
            if obj_company != company:
                raise Http404(f"La empresa {company} no es la misma empresa "
                    f"del objeto {obj_company}")
        
        # La empresa debe estar activa.
        if not company.is_active:
            raise Http404(f"La empresa {company} no está activa.")

        # El usuario debe tener acceso a esta empresa.
        if not company.user_has_access(self.request.user):
            raise Http404(
                f"El usuario {self.request.user} no pertenece a {company}")

        return obj

    def dispatch(self, request, *args, **kwargs):
        if self.error_list:
            raise ViewError(". ".join(error_list))

        if self.company_permission_required:

            if not request.user.has_company_permission(
                company=self.get_company(), 
                permission=self.company_permission_required):
                raise PermissionDenied(
                    "Acceso denegado. no tiene permisos suficientes.")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        company = self.get_company()
        context["user_company_permissions"] = user.get_company_permissions(company)
        context["user_company_groups"] = user.get_company_groups(company)
        return context


class BaseList(BaseView):

    VALUES_FOR_PAGINATE_BY = (20, 40, 60, 80, 100)
    list_display = [("__str__", _l("nombre"))]
    list_display_cssclass = {}

    def get_queryset(self):
        # Establecemos el valor al atributo 'paginate_by' si se especifica en la
        # url. Devolvemos el valor predeterminado si el valor no es válido.
        try:
            paginate_by = int(self.request.GET.get("paginate_by") or 
                self.paginate_by)
        except (ValueError, TypeError):
            paginate_by = self.VALUES_FOR_PAGINATE_BY[0]
        
        if not paginate_by in self.VALUES_FOR_PAGINATE_BY:
            paginate_by = self.VALUES_FOR_PAGINATE_BY[0]
            
        self.paginate_by = paginate_by

        qs = super().get_queryset()

        return QuerysetCapsule(view=self, queryset=qs)

    def get_list_display(self):
        return self.list_display or [("__str__", _l("nombre"))]

    def get_list_display_cssclass(self):
        return self.list_display_cssclass or {}
    

class BaseForm(BaseView):

    def get_form_kwargs(self):
        """Incluimos la instancia 'company' a los argumentos del formulario."""
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.get_company()
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        company = self.get_company()

        if not form.instance.pk:
            try:
                form.instance.create_user = user
            except (AttributeError):
                pass
            try:
                form.instance.company = company
            except (AttributeError):
                pass
        return super().form_valid(form)


class ListView(BaseList, generic.ListView):
    pass


class DetailView(BaseView, generic.DetailView):

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        return ObjectCapsule(self, obj)


class CreateView(BaseForm, generic.CreateView):
    pass


class UpdateView(BaseForm, generic.UpdateView):
    pass


class DeleteView(BaseView, generic.DeleteView):
    pass


class TemplateView(BaseView, generic.TemplateView):
    pass


# def view_decorator(company_field="company", company_in_url="company", 
#     pk_field="pk", pk_in_url="pk"):
#     """
#     Decorador para las vistas genéricas del proyecto Unolet.

#     La url de las mayoría de los objetos del proyecto, contiene el id de la 
#     empresa en la que se está trabajando, y de la cual pertenece el objeto que
#     en ese momento se está gestionando.

#     @view_decorator("company")
#     class MyDetailView(DetailView):
#         pass

#     Parameters:
#         company_field (str): nombre del campo en el modelo que contiene la 
#         referencia a la empresa.

#         company_in_url (str): nombre que identifica el pk de la empresa en la URL.

#         pk_field (str): nombre del campo en el modelo que contiene el pk del 
#         objeto que se va a obtener.

#         pk_in_url (str): nombre que  identifica el pk del objeto en la URL.
#         ----

#         El siguiente ejemplo buscará un objeto que coincida con sus campos 
#         'campany' y 'pk':

#             (model, {'company', kwargs['company'], 'pk': kwargs['pk']})
        
#         Este otro ejemplo el objeto en cuestión no tiene un campo 'company' pero 
#         tiene un related field ForeingKey de cual dicho objeto si lo tiene 
#         (suponiendo que el related field tiene el nombre de 'doctype'):

#             (model, {'doctype__company': kwargs['company'], 'pk': kwargs['pk']})

#         Este otro ejemplo el campo que contiene el pk en la URL se especificó 
#         con un nombre diferente a 'pk', por ejemplo 'warehouse':

#             (model, {'company': kwargs['company'], 'pk': kwargs['warehouse']})
#     """
#     from company.models import Company

#     VALUES_FOR_PAGINATE_BY = (20, 40, 60, 80, 100)

#     list_display = (("__str__", _l("Nombre")))

#     error_list = []

#     def get_company(view_instance):
#         try:
#             company = view_instance.request.company
#         except (AttributeError):
#             try:
#                 company = view_instance.get_context_data()["company"]
#             except (AttributeError, KeyError):
#                 company = get_object_or_404(Company, pk=kwargs[company_in_url])
#         return company

#     def get_list_display(view_instance):
#         return getattr(view_instance, "list_display", list_display)
            
#     def get_list_display_values(view_instance):
#         list_display = view_instance.get_list_display()
#         values = []
#         for obj in view_instance.object_list:
#             for attname, verbose_name in list_display:
#                 try:
#                     values.append(getattr(obj, attname))
#                 except (AttributeError):
#                     values.append(getattr(view_instance, attname))(obj)
#             yield values

#     def new_get_object(view_instance, queryset=None):

#         company = get_company(view_instance)
#         company_pk = view_instance.kwargs.get(company_in_url)
#         pk = view_instance.kwargs.get(pk_in_url)
        
#         if company_pk and pk:
#             filters = {company_field: company_pk, pk_field: pk}
#             obj = get_object_or_404(view_instance.model, **filters)
#         else:
#             obj = None

#         # La objeto debe pertenecer a la misma empresa obtenida por url.
#         if obj:
#             obj_company = functools.reduce(getattr, [obj] + company_field.split("__"))
#             if obj_company != company:
#                 raise Http404(f"La empresa {company} no es la misma empresa "
#                     f"del objeto {obj_company}")
        
#         # La empresa debe estar activa.
#         if not company.is_active:
#             raise Http404(f"La empresa {company} no está activa.")

#         # El usuario debe tener acceso a esta empresa.
#         if not company.user_has_access(view_instance.request.user):
#             raise Http404(f"El usuario {request.user} no pertenece a {company}")

#         return obj

#     def new_get_form_kwargs(view_instance):
#         """Incluimos la instancia 'company' a los argumentos del formulario."""
#         kwargs = super(view_instance.__class__, view_instance).get_form_kwargs()
#         kwargs["company"] = get_company(view_instance)
#         return kwargs

#     def new_form_valid(view_instance, form):
#         user = view_instance.request.user
#         company = get_company(view_instance)

#         if not form.instance.pk:
#             try:
#                 form.instance.create_user = user
#             except (AttributeError):
#                 pass
#             try:
#                 form.instance.company = company
#             except (AttributeError):
#                 pass
#         return super(view_instance.__class__, view_instance).form_valid(form)

#     def new_dispatch(view_instance, request, *args, **kwargs):

#         if error_list:
#             raise ViewError(". ".join(error_list))

#         company_permission_required = getattr(view_instance, 
#             "company_permission_required", None)

#         if (company_permission_required):
#             user = request.user
#             company = get_company(view_instance)

#             if not user.has_company_permission(company=company, 
#                 permission=company_permission_required):
#                 raise PermissionDenied("Acceso denegado. no tiene permisos suficientes.")

#         return super(view_instance.__class__, view_instance).dispatch(
#             request, *args, **kwargs)

#     def new_get_context_data(view_instance, **kwargs):
#         view_class = view_instance.__class__
#         context = super(view_class, view_instance).get_context_data(**kwargs)
#         user = view_instance.request.user
#         company = get_company(view_instance)
#         context["user_company_permissions"] = user.get_company_permissions(company)
#         context["user_company_groups"] = user.get_company_groups(company)
#         return context

#     def new_get_queryset(view_instance):
#         # Establecemos el valor al atributo 'paginate_by' si se especifica en la
#         # url. Devolvemos el valor predeterminado si el valor no es válido.
#         try:
#             paginate_by = int(view_instance.request.GET.get("paginate_by") or 
#                 view_instance.paginate_by)
#         except (ValueError, TypeError):
#             paginate_by = VALUES_FOR_PAGINATE_BY[0]
        
#         if not paginate_by in VALUES_FOR_PAGINATE_BY:
#             paginate_by = VALUES_FOR_PAGINATE_BY[0]
            
#         view_instance.paginate_by = paginate_by

#         return super(view_instance.__class__, view_instance).get_queryset()
    
#     def validate_view_class_attrs(view_class):
#         """Valida algunos attributos establecidos en la clase de la vista."""
#         if hasattr(view_class, "paginate_by"):
#             if view_class.paginate_by != None:
#                 if not view_class.paginate_by in VALUES_FOR_PAGINATE_BY:
#                     error_list.append(f"El valor del atributo 'paginate_by' "
#                         f"debe ser algunos de estos '{VALUES_FOR_PAGINATE_BY}', "
#                         f"pero se indicó '{view_class.paginate_by}'.")

#     def _generic_view_class_wrapper(view_class):

#         validate_view_class_attrs(view_class)

#         if hasattr(view_class, "get_object"):
#             view_class.get_object = new_get_object

#         if hasattr(view_class, "get_form_kwargs"):
#             view_class.get_form_kwargs = new_get_form_kwargs

#         if hasattr(view_class, "form_valid"):
#             view_class.form_valid = new_form_valid

#         if hasattr(view_class, "get_queryset"):
#             view_class.get_queryset = new_get_queryset

#         view_class.get_context_data = new_get_context_data
#         view_class.dispatch = new_dispatch
#         view_class.get_list_display = get_list_display
#         view_class.get_list_display_values = get_list_display_values

#         return view_class

#     return _generic_view_class_wrapper