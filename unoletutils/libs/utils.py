"""
Conjunto de utilidades.
"""
import copy
import warnings
import sys
from io import BytesIO
import datetime
from decimal import Decimal
import warnings
import functools
try:
    import barcode
    from barcode.writer import SVGWriter, ImageWriter
except (ImportError) as e:
    warnings.warn(e)
try:
    from django.utils.translation import gettext as _
    from django.utils.translation import gettext_lazy as _l
    from django.db import models
    from django.urls import reverse_lazy, NoReverseMatch
    from django.contrib.sites.models import Site
except (ImportError) as e:
    warnings.warg(e)

from . import text, json, icons


def valuecallable(obj):
    """Intentará invocar el objeto --> obj() y retorna su valor."""
    try:
        return obj()
    except (TypeError):
        return obj


def supergetattr(obj, name, default="", get_display_name=True):
    """
    Una función getattr con super poderes.

    Si el nombre 'name' contiene puntos (.) se asume que son varios Nombres
    uno es un método del otro en el mismo orden.

    Parameters:

        obj (object): Cualquier objeto.

        name (str):

    >> supergetattr(obj, 'a.b.c', False)
    a = obj.a() or obj.a
    b = a.b() or a.b
    c = b.c() or b.c

    >> supergetattr(obj, 'a.b')
    a = obj.a() or obj.a
    b = a.get_display_b() or a.get_display_b or a.b() or a.b

    >> supergetattr(obj, 'a')
    a = obj.get_a_display() or obj.get_a_display or obj.a() or obj.a
    """
    names = name.split(".")
    if get_display_name:
        name_end = names[-1]
        names[-1] = f"get_{names[-1]}_display"

    attr = obj
    for nam in names:
        try:
            attr = valuecallable(getattr(attr, nam))
        except (AttributeError):
            if get_display_name:
                attr = valuecallable(getattr(attr, name_end, default))
    return attr


def get_barcode(code: str, strtype: str="code128", render: bool=True, 
    options: dict=None):
    """
    Obtiene el código de barras con python-barcode.

    https://python-barcode.readthedocs.io/en/latest/
    https://pypi.org/project/python-barcode/

    Parameters:
        code (str): Código en string del barcode a obtener.

        strtype (str): 'code39', 'code128', 'ean', 'ean13', 'ean8', 'gs1',
        'gtin','isbn', 'isbn10', 'isbn13', 'issn', 'jan', 'pzn', 'upc', 'upca'

        render (bool): (default=True) le aplica el método 'render()' a la 
        salida, obteniendo así el contenido en string del SVG

        options (dict): (default={compress=True}) opciones que se pasarán al 
        render.

    Returns:
        barcode (object): barcode.get_barcode_class(strtype)(str(code)).render()
    """
    c = barcode.get_barcode_class(strtype)(str(code), writer=SVGWriter())
    if (render is True):
        opt = dict(compress=True)
        opt.update(options or {})
        return c.render(opt).decode("utf-8")
    return c


def upload_file_on_site(instance, filename):
    """
    Función para ser utilizada en campos de subida de archivo, para guardar el 
    archivo en una ruta ideal que contiene el nombre del site, aplicación y 
    modelo. 
    Ejemplo: 'www.misite.com/miapp/mimodel/filename'.
    """
    site = getattr(instance, "site", Site.objects.get_current())
    return "/".join([site.domain, instance.__class__._meta.app_label, 
        instance.__class__._meta.model_name, filename])


def upload_file_on_company(instance, filename):
    """
    Función para ser utilizada en campos de subida de archivos, para guardar el
    archivo en una ruta ideal que contiene el nombre del site, empresa, 
    aplicación y modelo. 
    Ejemplo: 'www.misite.com/company/miapp/mimodel/filename'.
    """
    site = getattr(instance, "site", Site.objects.get_current())
    company = getattr(instance.get_company(), "id", 0)
    return "/".join([site.domain, company, instance.__class__._meta.app_label, 
        instance.__class__._meta.model_name, filename])


class ModelBase(models.Model, text.Text):
    """
    Clase Django models.Model abstracto base para heredar en los modelos.
    """
    # Nombre del campo a la que apunta la empresa. Si este campo no está 
    # presente o depende de un campo relacionado, establezcalo en el modelo.
    # Por ejemplo: el modelo Document no posee campo 'company', sino que posee 
    # un campo relacionado 'doctype' el cual a su vez si posee uno 'company', 
    # entonces en el modelo Document esta variable la establecemos así:
    # COMPANY_FIELD_NAME = "doctype__company".
    COMPANY_FIELD_NAME = "company"

    list_display = [("__str__", _("nombre"))]

    # Campo de la empresa a la que pertenecerá...
    company = models.ForeignKey("company.Company", on_delete=models.CASCADE,
    verbose_name=_l("Empresa"))

    # Se utilizará como campo de búsqueda.
    # Si no desea incluirlo en el modelo haga: tags = None en el modelo.
    tags = models.CharField(max_length=700, blank=True, editable=False)

    class Meta:
        verbose_name = ""
        verbose_name_plural = ""
        abstract = True

    def __str__(self):
        return getattr(self, "name", None) or getattr(self, "pk", "ModelBase")

    def clean(self):
        try:
            self.tags = text.Text.get_tag(str(self), combinate=True)[:700]
        except (AttributeError):
            pass

    @property
    def verbose_name(self):
        return self.__class__._meta.verbose_name

    @property
    def verbose_name_plural(self):
        return self.__class__._meta.verbose_name_plural

    @classmethod
    def get_base_url_name(cls):
        return ("%s-%s" % (cls._meta.app_label, cls._meta.model_name)).lower()

    def get_reverse_kwargs(self, no_company=False):
        if (self.COMPANY_FIELD_NAME) and (not no_company):
            return {"company": self.get_company().pk, "pk": self.pk}
        return {"pk": self.pk}

    def reverse_lazy(self, url_name, **kwargs):
        kw = kwargs or self.get_reverse_kwargs()
        return reverse_lazy(url_name, kwargs=kw)

    def get_detail_url(self):
        return self.reverse_lazy("%s-detail" % self.get_base_url_name())

    def get_update_url(self):
        return self.reverse_lazy("%s-update" % self.get_base_url_name())

    def get_delete_url(self):
        return self.reverse_lazy("%s-delete" % self.get_base_url_name())

    def get_list_url(self):
        kwargs = self.get_reverse_kwargs()
        try:
            kwargs.pop("pk")
        except (KeyError):
            pass
        return self.reverse_lazy("%s-list" % self.get_base_url_name(), **kwargs)

    def get_create_url(self):
        kwargs = self.get_reverse_kwargs()
        try:
            kwargs.pop("pk")
        except (KeyError):
            pass
        return self.reverse_lazy("%s-create" % self.get_base_url_name(), **kwargs)

    def get_absolute_url(self):
        return self.get_detail_url() or self.get_update_url()

    def get_company(self):
        """Obtiene la empresa a la que pertenece este objeto."""
        return self.getattr(self.COMPANY_FIELD_NAME)

    def get_object_detail(self, exclude: list=[]):
        """Obtiene un diccionario con informacion de los campos y sus valores."""
        fields = self._meta.get_fields()
        out = []
        exclude = list(exclude) + ["id", "tags", "company_id"]
        #raise TypeError("\n\n".join([str(field.__dict__) for field in fields]))
        for field in fields:
            try:
                attname = field.attname
            except (AttributeError):
                continue
            
            if attname in exclude:
                continue 
        
            value = getattr(self, attname)
            display = value

            if getattr(field, "related_model", None):
                value = field.related_model.objects.get(id=value)
            
            try:
                display = getattr(self, f"get_{attname}_display")()
            except (AttributeError):
                if isinstance(field, (models.DecimalField, models.IntegerField, 
                    models.FloatField)):
                    display = f"{value:,}"

            out.append({"field": field, "value": value, "display": display})
        return out

    def save_without_historical_record(self, *args, **kwargs):
        """
        If you want to save a model without a historical record.

        https://django-simple-history.readthedocs.io/en/latest/querying_history.html
        
        """
        self.skip_history_when_saving = True
        try:
            out = super().save(*args, **kwargs)
        finally:
            try:
                del self.skip_history_when_saving
            except (AttributeError):
                pass
        return out

    def getattr(self, name, default="__raise_exception__"):
        """
        Un getattr ideal.

        Permitiendo obtener el valor de un campo relacionado a este objeto.
        Por ejemplo: Suponiendo que el objeto en cuestión tiene un campo
        ForeignKey llamado 'documento', el cual a su vez tiene un campo
        ForeignKey llamado 'almacen':
            obj.getattr('documento__almacen__nombre')

        Parameters:
            name (str): Nombre del attributo o field.

        Returns:
            getattr(name)
        """
        # Lanzará excepción si no se encuentra el primer nombre.
        # Pero para el resto, devolverá el valor del argumento 'default' 
        # si se indica.

        if name == "__str__":
            return str(self)

        names = name.split("__")
        attr = self
        for n in names:
            if (hasattr(attr, n)):
                attr = getattr(attr, n, None)
            else:
                if (default != "__raise_exception__"):
                    return default
                na = [a for a in attr.__dict__.keys() if not a.startswith("__")]
                raise AttributeError(
                    f"Error en {repr(self)} obteniendo el atributo '{name}'. "
                    f"{repr(attr)} no tiene un atributo llamado '{n}'. \n"
                    f"{na}.")
        return attr

    def get_list_display(self):
        return [self.getattr(e[0]) for e in self.list_display]

    def get_actions_links(self, size: str="1rem", fill: str=None, 
        defaults: list=None) -> dict:
        """Obtiene un diccionarios con las acciones para el objeto."""
        if not defaults:
            defaults = ["detail", "update", "delete"]

        out = {}
        for action in defaults:
            act = self.get_action(action, size=size, fill=fill)
            if act:
                out[action] = act
        return out

    def get_action(self, action: str, size: str="1rem", fill: str=None) -> dict:
        """Obtiene la acción crear."""

        info = {
            "create": {
                "name": _("Nuevo"), 
                "icon": icons.svg("plus-circle-fill", size=size, 
                    fill=fill or "var(--bs-success)", on_error=icons.DEFAULT)}, 
            "update": {
                "name": _("Modificar"), 
                "icon": icons.svg("pencil-fill", size=size, 
                    fill=fill or "var(--bs-warning)", on_error=icons.DEFAULT)}, 
            "delete": {
                "name": _("Eliminar"), 
                "icon": icons.svg("x-circle-fill", size=size, 
                    fill=fill or "var(--bs-danger)", on_error=icons.DEFAULT)}, 
            "list": {
                "name": _("Lista"), 
                "icon": icons.svg("card-list", size=size, 
                    fill=fill or "var(--bs-dark)", on_error=icons.DEFAULT)}, 
            "detail": {
                "name": _("Detalle"), 
                "icon": icons.svg("eye-fill", size=size, 
                    fill=fill or "var(--bs-primary)", on_error=icons.DEFAULT)}, 
        }

        try:
            url = str(getattr(self, f"get_{action}_url")())
        except (NoReverseMatch):
            return None

        item = info[action]
        item["url"] = url

        return item

    def get_barcode(self, code=None, strtype="code128"):
        """
        Obtiene el código de barras de este objeto.
        según su salida str.

        Parameters:
            code (str): código a obtener (opcional) (default = self)

            strcode (str): tipo de código.

        Returns:
            get_barcode(code=str(code or self), strtype=strtype)
        """
        try:
            return get_barcode(str(code or self), strtype=strtype)
        except (BaseException) as e:
            return e

    def get_this(self):
        """
        Obtiene este objeto desde la base de datos.

        Útil en caso de modificaciones, para comparar los datos anteriores con 
        los que se pretenden establecer.
        """
        if self.pk:
            return self.__class__.objects.get(pk=self.pk)

    def to_dict(self, to_json: bool=False, for_json: bool=False, 
        no_json_serialize_to_str: bool=False):
        """
        Obtiene un diccionario con los nombres de los campos como claves,
        y otro diccionario como valores, con algunos valores de la field.

        Parameters:
            to_json = True: devolverá un objeto Json.

            for_json = True: devolverá un diccionario válido para ser 
            serializado a json.

            no_json_serialize_to_str = True: Para los campos que no sean 
            serializados a json, serán convertidos a string mediante str(value).
        """
        out = {}
        fields = self.GetFields()
        for field in fields:

            value = getattr(self, field.name, None)

            if (to_json) or (for_json):

                if (isinstance(value, Decimal)):
                    value = float(value)

                # Los campos que no se puedan serializar a Json,
                # no serán incluidos.
                try:
                    json.dumps(value)
                except (TypeError):
                    if (not no_json_serialize_to_str):
                        value = str(value)
                    else:
                        continue

            out[field.name] = {
                "name": field.name,
                "verbose_name": field.verbose_name,
                "value": value,
                "editable": field.editable,
            }

        if (to_json):
            return json.dumps(out)
        return out

    def to_json(self):
        """Obtiene un objeto tipo Json con los datos de los campos."""
        return self.ToDict(to_json=True)

    @classmethod
    def get_img_without_default(cls):
        """Igual que cls.get_img pero sin default atributo."""
        return cls.get_img(default="")

    @classmethod
    def get_img(cls, default="/static/icons/file-text.svg"):
        """
        Trata de obtener la ruta de la imagen asignada a este objecto o modelo.
        De no encontrar una ruta de imagen, devolverá el valor del parámetro 
        default.
        """
        # Buscamos una field (campo) de tipo image o file
        #  que se hay declarado con algunos de estos nombres.
        field = getattr(cls, "image", 
                getattr(cls, "img", 
                getattr(cls, "icon", 
                getattr(cls, "logo", 
                getattr(cls, "photo", object)))))

        return getattr(field, "url", "") or default

    def get_history(self):
        """
        Obtiene el historial de cambios realizados a este objeto con 
        'django-simple-history'.
        """
        try:
            return self.history.all()
        except (AttributeError) as e:
            warnings.warn(e)

    def get_history_all(self):
        """
        Obtiene el historial de cambios realizados a todos
        los objetos del modelo, con 'django-simple-history'.
        """
        try:
            return self.history.model.objects.all()
        except (AttributeError) as e:
            warnings.warn(e)
