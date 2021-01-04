"""
Módulo base para los reportes.

"""

from django.utils.translation import gettext as _

from fuente import (csv, exceptions, fecha, html, json, number, pdf, text,
    utils, var)
from fuente.report.fields import (FieldBase, FloatField, DecimalField,
    IntegerField,TextField, DateField, DateTimeField, BooleanField)
from fuente.report.forms import FormSearch



class ReportError(Exception):
    """Errores para los reportes."""



class ReportLocked(ReportError):
    """Excepción cuando el reporte está bloqueado porque se está generando."""



class ReportDoesNotExist(ReportError):
    """Error cuando se intenta obtener un reporte que no existe."""



class ReportsGenerates():
    """
    Guarda instancias de los reportes generados para la sessión actual.

    Útil para cuando un usuario ha generado un reporte, pero salió de la página,
    etc., dejango el reporte generandose en el servidor. Pues cuando el usuario
    regrese a la página donde se genera el mismo reporte, el sistema le mostrará
    el que ha dejado.

    """
    # {id: report_instance} id = Identificador único.
    data = {}

    def __getitem__(self, id):
        return self.Get(id)

    def __iter__(self):
        for queryset in self.data:
            yield queryset

    @classmethod
    def Add(self, queryset, totals):
        self.data[self.queryset] = totlas

    @classmethod
    def Get(self, queryset):
        return self.reports_instances[queryset]



class ReportBase:
    """
    Clase base para todos los tipos de reportes.
    """



class Report(ReportBase):
    """
    Clase base para la creación de reportes a partir de modelos.
    
    """
    lock = False
    lock_instance = None
    lock_instance_report = None
    request = None
    user_id = None
    progress = 0
    progress_max = 0
    stop = False # Se usa para detener el bucle en __iter__

    # Determina si el reporte ya ha sido generado, esto es si ya ha pasado por
    # __iter__ y se realizaron todos los cálculos de lugar. Usaremos esta
    # variable para saber si lo generamos (lento) o no (rápido).
    generated = False


    def __init__(self, item_class, request, queyrset=None, **kwargs):
        self.item_class = item_class
        self.request = request
        self.user_id = request.user.id
        self.queryset = queyrset
        #self._totals = item_class.meta().totals.copy()

        self.title = kwargs.get("title") or self.item_class.meta().title
        self.description = kwargs.get("description") or self.item_class.meta().description
        self.img = kwargs.get("img") or self.item_class.meta().img

        #self.filter_from_form_data(request)


    def __str__(self):
        return self.item_class.meta().title

    def __iter__(self):

        if self.__class__.lock:
            if self.__class__.lock_instance == self.item_class:
                if self.__class__.user_id == self.request.user.id:
                    raise ReportLocked(f"{self.request.user} está generando un reporte "
                        f"para '{self.__class__.lock_instance.meta().title}'. Avance "
                        f"{self.__class__.progress} de {self.__class__.progress_max}.")

        self.__class__.lock = True
        self.__class__.lock_instance = self.item_class
        self.__class__.lock_instance_report = self
        self.__class__.user_id = self.request.user.id
        self.__class__.progress_max = self.queryset.count()
        self.__class__.progress = 0

        Id = id(self)

        if True is True:
            self.ClearTotals()
            print("Generando reporte", f"{Id=}", str(self))
            for obj in self.queryset:

                if self.__class__.stop:
                    print("Reporte detenido...")
                    break

                item = self.item_class(obj, report=self)
                self.__class__.progress += 1

                print(str(self), f"[{Id=}]", self.__class__.progress, "/",
                self.__class__.progress_max, end="\r")

                yield item

        print("Reporte generado.", f"{Id=}", str(self))
        self.__class__.stop = False
        self.__class__.lock = False
        self.__class__.lock_instance = None
        self.__class__.lock_instance_report = None
        self.__class__.user_id = None
        self.__class__.generated = True

    def __len__(self):
        return self.queryset.count()

    @classmethod
    def cancel(self):
        """
        Detiene el proceso de generación en curso de este reporte.
        """
        self.stop = True

    def has_detail(self):
        """
        Retorna True, si este reporte tiene detalles declarados.
        """
        if self.item_class.meta().has_detail:
            return True
        return False

    def to_json(self):
        """
        Obtiene un dicionario (validado a json) con los datos de este reporte.
        """
        return {
            "title": self.title,
            "description": self.description,
            "img": self.img,
            "objs": [e.to_json() for e in self],
            "totals": {k:{"title": str(v), "objs": v.to_json()} for k,v in self.item_class.meta().totals.items()},
            "charts": self.item_class.meta().charts,
            "fields": {k:v.to_json() for k,v in self.item_class.get_fields().items()},
            "has_detail": self.has_detail(),
            "count": len(self),
            "columns_lenght": len(self.item_class.get_fields()),
        }

    def filter_from_form_data(self, request):
        """filtra desde la data form_search"""
        form_data = dict(request.GET)
        for key in form_data:
            value = form_data[key]
            try:
                self.filter(**{f"{key}__in": value})
            except (TypeError) as e:
                raise TypeError(e, key, value)

    def all(self, *args, **kwargs):
        """
        Actualiza el queryset con self.queryset.all(*args, **kwargs)
        """
        if self.queryset is None:
            self.queryset = self.item_class.meta().model.objects.all(*args, **kwargs)
        else:
            self.queryset = self.queryset.all(*args, **kwargs)
        return self

    def filter(self, *args, **kwargs):
        """
        Actualiza el queryset con self.queryset.filter(*args, **kwargs)
        """
        if self.queryset is None:
            self.queryset = self.item_class.meta().model.objects.filter(*args, **kwargs)
        else:
            self.queryset = self.queryset.filter(*args, **kwargs)
        return self

    def exclude(self, *args, **kwargs):
        """
        Actualiza el queryset con self.queryset.exclude(*args, **kwargs)
        """
        if self.queryset is None:
            self.queryset = self.item_class.meta().model.objects.exclude(*args, **kwargs)
        else:
            self.queryset = self.queryset.exclude(*args, **kwargs)
        return self

    def order_by(self, *args, **kwargs):
        """
        Actualiza el queryset con self.queryset.order_by(*args, **kwargs)
        """
        if self.queryset is None:
            self.queryset = self.item_class.meta().model.objects.all()
        self.queryset = self.queryset.order_by(*args, **kwargs)
        return self

    def none(self, *args, **kwargs):
        """
        Actualiza el queryset con self.queryset.none(*args, **kwargs)
        """
        if self.queryset is None:
            self.queryset = self.item_class.meta().model.objects.none(*args, **kwargs)
        else:
            self.queryset = self.queryset.none(*args, **kwargs)
        return self

    @classmethod
    def NoneReport(self):
        return NoneReport(self.item_class)

    def totals(self):
        """
        Retorna el listado de totales definidos.
        """
        return self.item_class.meta().totals

    def UpdateTotals(self):
        """
        Calcula los totales definidos.
        """
        for key in self.item_class.meta().totals:
            self.item_class.meta().totals[key].SetReport(self)
        return self.item_class.meta().totals

    def ClearTotals(self):
        """
        Limpia los totales calculados en los totales.
        """
        for key in self.item_class.meta().totals:
            self.item_class.meta().totals[key].clear()




class NoneReport(Report):
    """Reporte con valor nulo."""

    def __init__(self, item_class):
        self.item_class
        if item_class:
            self.title = item_class.meta().title
            self.description = item_class.meta().description
            self.img = item_class.meta().img

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except (AttributeError):
            return ""




class Total:
    """
    Representa un total de un reporte.
    """
    def __init__(self, *fields, **kwargs):
        """
        Parameters:
            fields (tuple): campos a mostrar ((name, verbose_name), ...)

        Keyword parameters:
            report (Report): reporte al quer pertenece este total.
            title (str): título del total.

        """
        self._report = kwargs.get("report", None)
        self._title = kwargs.get("title", None)
        self._fields_original = fields
        self._fields = {item[0]: {"verbose_name": item[1], "value": 0} for item in fields}

    def __str__(self):
        return str(self._title)

    def __iter__(self):
        # Cada item es un diccionario {'verbose_name': str, 'value': number}
        for name in self._fields:
            yield self._fields[name]

    def __getattribute__(self, name):
        # Primero se buscará en el diccionario self._fields. Si no existe tal 
        # clave, se buscará en este objeto.
        try:
            return object.__getattribute__(self, "_fields")[name]
        except (KeyError):
            return object.__getattribute__(self, name)

    def to_json(self):
        """
        Retorna un diccionario con los datos de este total.
        """
        return json.clean(self._fields)

    def clear(self):
        """
        Limpia los datos previamente calculados en este total poniendolos en 0.
        """
        self._fields = {
            item[0]: {"verbose_name": item[1], "value": 0}
            for item in self._fields_original
        }

    def calculate_all(self):
        """
        Calcula los campos establecidos en este total.
        """
        self.clear()
        for item in self._report:
            self.sum(item)
        return self

    def SetReport(self, report):
        """
        Establece el reporte al que pertenece este total.
        """
        self._report = report

    def sum(self, item):
        """
        Obtiene el valor correspondiente de 'item' y lo suma a este total.
        """
        for name in self._fields:
            result = getattr(item, name) + self._fields[name]["value"]
            self._fields[name]["value"] = result




class TotalFor(Total):
    """
    Tipo de total para reportes, que realiza la suma condicionalmente para 
    cada item que cumpla la condición de forma dividida.

    Útil si queremos obtener un total que muestre la sumatoria total para cada
    tipo de facturas en el reporte. etc.
    """

    def __init__(self, field="", fieldvalue="", **kwargs):
        super().__init__(**kwargs)
        self._field = field
        self._fieldvalue = fieldvalue

    def sum(self, item):
        """
        Suma el valor del item a su grupo correspondiente en este total.
        """
        field = str(getattr(item, self._field))
        fieldvalue = getattr(item, self._fieldvalue)
        try:
            self._fields[field]["value"] = fieldvalue + self._fields[field]["value"]
        except (KeyError):
            self._fields[field] = {"verbose_name": str(field), "value": fieldvalue}




class ModelReportMetaClassManager:
    """
    Esta clase es una especie de manejador para las clases Meta declaradas en
    los modelos de reportes.

    La clase Meta necesita tener los siguientes atributos:
        :model (django.db.models.Model)
        :title (str)
        :description (str)
        :img (str)
        :totals (dict): keys (str), values (Total, TotalFor)
        :charts (list): [('total_key', 'html_element_id'), ...]
        :form_search (FormSearch)

    """
    model = None
    title = _("Reporte")
    description = ""
    img = var.IMG_REPORTE
    totals = {}
    # [('total_key', 'html_element_id', options_dict, 'type'), ...] 
    # Ej.: [('total1', 'div1', {'title': 'Title', 'width': 400}, 'PieChart')]
    # Para las opciones del gráfico ver:
    # https://developers.google.com/chart/interactive/docs/gallery/piechart
    charts = []
    form_search = FormSearch()
    has_detail = False

    def __init__(self, metaclass):
        self.metaclass = metaclass

    def __getattribute__(self, name):

        if name == "metaclass":
            return object.__getattribute__(self, "metaclass")
        try:
            return getattr(self.metaclass, name)
        except (AttributeError):
            return super().__getattribute__(name)
    
    def __call__(self, *args, **kwargs):
        return self




class ModelReport:
    """
    Clase base de donde heredarán los demás reportes que configuremos.

    Un ModelReport es un modelo de representación de datos. Cada fila del 
    reporte generado tendrá como celdas (columnas) los campos que en este modelo
    declaremos.

    Las condiciones de búsqueda (filtro) varia para cada reporte declarado, por
    lo cual será necesario sobrescribir el método 'self.generate(request)' para
    adaptarlo a este reporte. El método debe obtener el reporte con
    super().generate(request), y luego ir filtrando el mismo y retornar el
    reporte filtrado.

    """

    class Meta:
        """
        La clase Meta necesita tener los siguientes atributos:
            :model (django.db.models.Model)
            :title (str)
            :description (str)
            :img (str)
            :totals (dict): keys (str), values (Total, TotalFor)
            :charts (list): [('total_key', 'html_element_id'), ...]
            :form_search (FormSearch)
        """
        model = None
        title = _("Reporte")
        description = ""
        img = var.IMG_REPORTE
        totals = {}
        charts = []
        form_search = FormSearch()
        has_detail = False

    def __init__(self, obj, report):
        """
        Cada instancia creada de este modelo de clases, se hará en la iteración
        del objeto Report, iterando sobre el queryset y pasando cada objeto
        (obj) y la instancia de dicho objeto Report (report).

        """
        self._obj = obj
        self._report = report

        for key in self._meta.totals:
            self.Meta.totals[key].sum(self)

    def __str__(self):
        return str(self._obj)

    def __getattribute__(self, name):

        if name == "_meta":
            return object.__getattribute__(self, "meta")()

        # Intentamos obtener el atributo de este objeto. De no encontrarlo, 
        # intantaremos obtenerlo del objeto instanciado self._obj.
        # Es posible especificar subfields separandolas con un punto. Ej.:
        #    'campo.subcampo.subcampo'
        try:
            attr = object.__getattribute__(self, name)
        except (AttributeError):
            attr = utils.supergetattr(self._obj, name)
            return utils.valuecallable(attr)

        # Si el atributo encontrado es un campo (Field) del reporte, enctonces
        # establecemos el valor a dicha field y la retornamos con el valor.
        # El valor lo obtenemos del self._obj, con el nombre del parámetro 
        # especificado en la field como 'origen'.
        if isinstance(attr, FieldBase):
            field = attr
            attr = utils.supergetattr(self._obj, attr.origen)
            attr = utils.valuecallable(attr)
            field.value = attr
            return field

        return attr

    @classmethod
    def meta(self):
        """
        Retorna la clase Meta donde están configuradas las opciones del reporte.
        """
        return ModelReportMetaClassManager(self.Meta)

    @property
    def data(self):
        return self.to_json()

    def to_json(self):
        """
        Retorna un diccionario con los datos de este modelo de reporte.
        """
        out = {"fields": self.get_fields(), "detail": None}

        for attrname in out["fields"]:
            out["fields"][attrname] = getattr(self, attrname).to_json()

        if self.meta().has_detail:
            out["detail"] = self.get_detail().to_json()

        return out

    @classmethod
    def create(self, request):
        """
        Crea una instancia de Report, o devuelve la instacia si ya el usuario
        la ha creado.
        """
        if Report.lock_instance == self:
            self._report = Report.lock_instance_report
        else:
            self._report = Report(self, request)
        return self._report

    @classmethod
    def report(self):
        """
        Obtiene el reporte creado, o crea una nuevo si no está creado.
        """
        return getattr(self, "_report", self.create())

    @classmethod
    def none(self):
        """
        Retorna un reporte nulo.
        """
        return self.report().none()

    @classmethod
    def GetImg(self):
        """
        Obtiene la imagen establecida en este modelo.
        """
        return self._obj.GetImg()

    @classmethod
    def get_fields(self):
        """
        Obtiene los campos declaramos en este modelo.
        """
        return {k:f for k,f in self.__dict__.items() if isinstance(f, FieldBase)}

    @classmethod
    def get_fieldsnames(self):
        """
        Obtiene el nombre leíble de los campos de este modelo.
        """
        return [f.verbose_name for f in self.get_fields().values()]

    def get_detail(self, obj):
        """
        Obtiene el detalle configurado para el objeto pasado.

        Esta función debe declararse en cada modelo.

        def get_detail(self, obj):
            detail = OtherReport.generate()
            detail.filter(obj=obj)
            return detail

        """
        print(f"No ha declarado este método en el reporte {self}. {self.get_detail.__doc__}.")

    @classmethod
    def generate(self, request):
        """
        Crea el reporte, y filtra los items según el request.GET

        Este método lo podemos poner en cada reporte creado para establer
        el comportamiento para cada reportes.
        
        """
        return self.create(request).all()


