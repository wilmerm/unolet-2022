import warnings

from django.db import models
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l
from django.urls import reverse_lazy, NoReverseMatch

from unoletutils.libs import utils, text, icons


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
                else:
                    display = str(value)

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
                na = [a for a in getattr(attr, "__dict__", dict()).keys() if not a.startswith("__")]
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
        """Obtiene la acción indicada."""

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
        REESCRIBIR ESTE MÉTODO."""

    def to_json(self):
        """Obtiene un objeto tipo Json con los datos de los campos."""
        return self.to_dict(to_json=True)

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
                getattr(cls, "photo", 
                getattr(cls, "ICON", default))))))
        return getattr(field, "url", field)

    def get_create_user(self):
        """
        Obtiene el usuario que créo el registro.
        Primero consulta el campo 'create_user', y luego en el historial.
        """
        if hasattr(self, "create_user"):
            return self.create_user
        first_history = self.get_create_history()
        if first_history:
            return first_history.history_user

    def get_create_date(self):
        """
        Obtiene la fecha en que se creó el registro.
        Primero consulta el campo 'create_date', y luego en el historial.
        """
        if hasattr(self, "create_date"):
            return self.create_date
        first_history = self.get_create_history()
        if first_history:
            return first_history.history_date

    def get_create_history(self):
        """Obtiene el registro historico correspondiente a la creación."""
        history_qs = self.get_history()
        if history_qs != None:
            return history_qs.filter(history_type="+").first()

        # Si no existe un historial, se intentará retornar un diccionario con 
        # los valores de create_user y create_date si existen.
        elif hasattr(self, "create_user"):
            return {
                "history_user": self.create_user, 
                "history_date": getattr(self, "create_date", "")
            }

    def get_last_update_history(self):
        """Obtiene el registro historico de la última modificación."""
        history_qs = self.get_history()
        if history_qs != None:
            return history_qs.filter(history_type="~").last()

        # Si no existe un historial, se intentará retornar un diccionario con 
        # los valores de create_user y create_date si existen.
        elif hasattr(self, "update_user"):
            return {
                "history_user": self.update_user, 
                "history_date": getattr(self, "update_date", "")
            }

    def get_history(self):
        """
        Obtiene el historial de cambios realizados a este objeto con 
        'django-simple-history'.
        """
        try:
            return self.history.all().order_by("-history_date")
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
    
    def has_history(self):
        """Comprueba si este objeto posee historial de cambios."""
        if not hasattr(self, "history"):
            return False
        return bool(self.history.count())

