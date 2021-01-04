

import datetime
from decimal import Decimal
from functools import reduce
from django.utils import timezone
from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.urls import reverse, reverse_lazy, NoReverseMatch
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.db import models

from .var import *
from . import utils, text, html



def _(texto):
    return texto



def format_dict(value_dict):
    """
    Formatea el valor indicado según su tipo.
    """
    if (isinstance(value_dict, dict)):
        items = tuple([(e[0].replace("_", " ").title(), format_dict(e[1])) for e in value_dict.items()])
        return dict(items)
    return value_dict


class Obj(text.Text):

    def __init__(self, reporte, obj):
        self.reporte = reporte
        self.obj = obj
        self.GetImg = self.GetImg()

    def __str__(self):
        return str(self.obj)

    def __iter__(self):
        for value in self.GetValues():
            yield value

    def __getattribute__(self, name):
        if (name == "__str__"):
            return str(self.obj)
        if (name == "__repr__"):
            return repr(self.obj)

        # Buscamos primero en el objeto actual.
        try:
            return object.__getattribute__(self, name)
        except (AttributeError):
            pass

        # Buscamos en el reporte.
        try:
            attr = getattr(self.reporte, name)
        except (AttributeError):
            # Buscamos en los nombres que se indicaron en las fields.
            attr = "__NOATTRIBUTE__"
            for key, _field in self.reporte.__dict__.items():
                if isinstance(_field, Field):
                    if (_field.name == name):
                        attr = _field
                        try:
                            attr = attr()
                        except (TypeError):
                            pass
                        break

        if (attr == "__NOATTRIBUTE__"):
            # Buscamos en la instancia del modelo.
            try:
                attr = getattr(self.obj, name)
            except (AttributeError):
                attr = "__NOATTRIBUTE__"
            else:
                try:
                    return attr()
                except (TypeError):
                    return attr

        if (attr == "__NOATTRIBUTE__"):
            raise AttributeError("{} no tiene un atributo nombrado '{}'. \n{}".format(self, name, ", ".join(getattr(self, "__dict__", {}).keys())))

        if isinstance(attr, Field):
            _field = attr
            attr_name = attr.name
            attr_list = [attr_name]
            if ("." in attr_name):
                attr_list = attr_name.split(".")
                attr_name = attr_list[0]

            attr = self.obj
            for attr_name in attr_list:
                if (attr is None):
                    break
                else:
                    # Verificamos que el objeto tenga un atributo tratándolo de distintos modos:
                    # 1ro. Verificamos si es un atributo normal.
                    try:
                        attr = getattr(attr, attr_name)
                    except (AttributeError):
                        # 2do. Si falló en la busqueda del atributo, verificamos si es la clave de un diccionario.
                        try:
                            attr = attr[attr_name]
                        except (BaseException):
                            raise AttributeError("{} no tiene un attributo nombrado '{}' para {}. Falló en '{}'. \n{}".format(self, ".".join(attr_list), attr, attr_name, ", ".join(getattr(attr, "__dict__", {}).keys())))
                    # Es posible que el atríbuto sea un método. De ser así le 
                    # pasamos los argumentos que se definieron en la declaración de la Field.
                    try:
                        attr = attr(*_field.func_args, **_field.func_kwargs)
                    except (TypeError):
                        pass
            if (attr is self.obj):
                raise AttributeError("{} no tiene un atributo de nombre '{}'. {} {}. \n{}.".format(self, name, attr, ".".join(attr_list), ", ".join(getattr(attr, "__dict__", {}).keys())))
            try:
                return attr(*_field.func_args, **_field.func_kwargs)
            except (TypeError):
                return attr

        return attr

    def GetImg(self):
        try:
            return self.obj.GetImg()
        except (AttributeError):
            return ""

    def get_absolute_url(self):
        """Reemplaza el método del modelo, para que coincida con algun otro
        especificado en el reporte a través del attributo 'absolute_url_method, cuyo 
        valor es un string con el nombre del método que se llamará en lugar del 
        metodo predeterminado 'get_absolute_url'. Si el modelo en cuestión no cuenta
        con la declaración de este método, se retorna un string vacio.

        Si el nombre del método indicado está idealmente dividido por punto(s) '.',
        entonces se entenderá que pretendemos llamar el metodo de un objeto relacionado
        a este. Ejemplo: 'documento.almacen.get_absolute_url', con este string deducimos
        que el actual objeto tiene un campo llamado 'documento' que resulta ser a su vez 
        otro objeto ya que este tiene otro método llamado 'almacen', entonces llamamos el 
        método 'get_absolute_url() del objeto 'almacen'."""
        if ("." in self.reporte.absolute_url_method):
            attr_list = self.reporte.absolute_url_method.split(".")
        else:
            return getattr(self.obj, self.reporte.absolute_url_method, str)()
        attr = self.obj
        for attr_name in attr_list:
            # Obtenemos el atributo.
            # Verificamos si el atributo que se indicó es un método o no.
            try:
                attr = getattr(attr, attr_name)()
            except (TypeError):
                attr = getattr(attr, attr_name)
            # Si el valor del atributo obtenido es nulo (NoneType), 
            # retornamos un string vacio, ya que esto podría deberse a que 
            # el campo relacionado este vacio o nulo.
            if (attr == None):
                return ""
        return attr

    def GetValues(self):
        """
        Retorna los valores correspondientes a las fields declaradas.
        """
        fields = self.reporte.GetFields()
        out = []
        for field in fields:
            out.append(getattr(self, field.name))
        return out

    def GetFields(self):
        fields = self.reporte.GetFields()
        for field in fields:
            field.SetValue(getattr(self, field.name))
            yield field

    def GetDetalle(self):
        detalle = self.reporte.detalle
        detalle_fieldname = self.reporte.detalle_fieldname
        if (detalle == None):
            return
        if (not detalle_fieldname):
            raise ValueError("No se establecio, en el atributo 'detalle_fieldname', el nombre de la field que relaciona a '{}' con '{}'".format(detalle, self.reporte))
        detalle.SetQueryset(detalle.GetModel().objects.filter(**{self.reporte.detalle_fieldname: self.obj}))
        return detalle






class Field(text.Text):

    def __init__(self, parent=None, name="", verbose_name=None,  datatype=STR, cssclass="left", 
    colspan=1, truncatechars=None, decimal_places=2, func_args=[], func_kwargs={}):

        self.parent = parent # Objeto padre que contiene esta field.
        # :: name:
        # Podemos indicar subfield dividiendolas por un punto (.).
        #     Ejemplo: fieldname.subfield
        # Tambien podemos indicar metodos del objeto en cuestión.
        #     Ejemplo: fieldname.subfield.GetValue
        self.name = name # Nombre del campo en la base de datos.
        self.datatype = datatype # Tipo de dato del valor.
        self.colspan = colspan # Cuantas columnas ocupará esta field en la tabla HTML de la plantilla.
        self.truncatechars = truncatechars # Límita el número de caracters del valor para el método __str__
        self.decimal_places = decimal_places
        # :: func_args y func_kwargs:
        # Estos dos parámetros serán pasados a la función que se especifique en 'name' de ser una función.
        # Ejemplo: fieldname.subfield.GetName(*func_args, **func_kwargs)
        self.func_args = func_args
        self.func_kwargs = func_kwargs

        # Nombre leible de la columna.
        if verbose_name is None:
            self.verbose_name = self.name.title().replace("_", " ")
        else:
            self.verbose_name = verbose_name
        # Clases CSS que se aplicarán en la plantilla.
        self.cssclass = cssclass.strip()
        if (datatype in (INT, FLOAT, DECIMAL)):
            self.cssclass = self.cssclass.replace("left", "")
            self.cssclass += " text-right text-nowrap"
        if (datatype in (DATE, DATETIME)):
            self.cssclass += " text-nowrap"
        self.cssclass = self.cssclass.strip()
        # Valor predeterminado según el tipo de valor especificado.
        if datatype == INT:
            self.value = int()
        elif datatype == FLOAT:
            self.value = float()
        elif datatype == DECIMAL:
            self.value = Decimal()
        elif datatype == STR:
            self.value = ""
        elif datatype == HTML_IMAGE:
            self.value = html.img(src="")
        else:
            self.value = None

    def __str__(self):
        if (self.value is None):
            value = ""
        if (self.value == UNDEFINED):
            return ""
        if (self.value is False):
            return _("No")
        elif (self.value is True):
            value = _("Si")
        elif (self.datatype in (FLOAT, DECIMAL)):
            try:
                value = "{:,.2f}".format(round(float(str(self.value)), self.decimal_places))
            except (ValueError):
                value = str(self.value)
        elif (self.datatype == INT):
            value = "{}".format(self.value)
        elif (self.datatype == HTML_IMAGE):
            value =  str(self.value)
        elif (isinstance(self.value, datetime.datetime)):
            value = self.value.strftime("%d-%m-%Y %H:%M:%S")
        elif (isinstance(self.value, datetime.date)):
            value = self.value.strftime("%d-%m-%Y")
        else:
            value = str(self.value)

        if self.truncatechars:
            long_value = value
            value = value[:self.truncatechars]
            dif = len(long_value) - len(value)
            if dif > 3:
                value += "..."
            else:
                value = long_value

        return value

    def __repr__(self):
        return "{}({})".format(self.name, self.value)

    def html(self):
        tag = html.span()
        style = ""
        if (self.datatype in (FLOAT, DECIMAL)):
            try:
                value = float(str(self.value))
                if value < 0:
                    style = "color: red"
            except (ValueError):
                pass

        elif (self.datatype == INT):
            try:
                if int(self.value) < 0:
                    style = "color: red"
            except (ValueError):
                pass

        elif (self.datatype == HTML_IMAGE):
            return str(self.value)

        value = self.__str__()

        tag.AppendChild(value)
        tag.SetAttr("style", style)
        return tag

    def __setattr__(self, name, value):
        if name == "value":
            return self.SetValue(value)
        return super().__setattr__(name, value)

    def SetValue(self, value):
        if isinstance(value, Field):
            self = value

        elif (value == None):
            self.__dict__["value"] = ""

        elif (value == UNDEFINED):
            self.__dict__["value"] = UNDEFINED

        elif self.datatype == STR:
            self.__dict__["value"] = str(value)

        elif self.datatype == INT:
            self.__dict__["value"] = int(value)

        elif self.datatype == FLOAT:
            self.__dict__["value"] = float(value)

        elif self.datatype == DECIMAL:
            try:
                self.__dict__["value"] = Decimal(str(value))
            except (BaseException) as e:
                raise ValueError(f"{e}. value={value}, type={type(value)}")

        elif self.datatype == (HTML_IMAGE):
            self.__dict__["value"] = html.img(src=str(value))

        elif (self.datatype == DICT) or (isinstance(value, dict)):
            self.__dict__["value"] = format_dict(value)
            
        else:
            try:
                self.__dict__["value"] = value()
            except (BaseException):
                self.__dict__["value"] = value

        try:
            if float(value) < 0:
                self.cssclass += " negativo"
            else:
                self.cssclass = self.cssclass.replace("negativo", "").strip()
        except (ValueError, TypeError):
            pass

    def GetValue(self):
        return self.value




class Reporte(ListView, text.Text):
    """
    Clase base para la creación de reportes. 
    Un objeto reporte es útil para mostrar un listado de datos, 
    así como, por supuesto, un reporte o informe.
    """

    def __init__(self, parent=None, model=None, name=None, 
    description=_("Reporte..."), queryset=None, paginate_by=100):

        ListView.__init__(self)

        # Métodos del ListView y modelo
        self.model = self.__class__.model or model
        self.paginate_by = self.__class__.paginate_by or paginate_by

        self.absolute_url_method = "get_absolute_url"
        self.absolute_url_target = "" # se usará en el atributo HTML target.

        self.__dict__["_parent"] = parent
        self.__dict__["_name"] = name or getattr(model, "_meta.verbose_name_plural", None)
        self.__dict__["__description"] = description
        self.__dict__["_fields"] = {} # Diccionario con los nombres de fields declaradas para encontrarlas facilmente por su nombre.
        self.__dict__["_totales_fields"] = []
        self.__dict__["_rowcssclass"] = "row1"
        self.__dict__["detalle"] = None # Otro reporte que se relaciona con este.
        self.__dict__["detalle_fieldname"] = "" # Nombre de la field que relaciona este reporte con el especificado en 'detalle'
        self.__dict__["_has_encabezado"] = True # Determina si se mostrará o no el encabezado (nombres de las columnas)
        try:
            if (not model):
                model = queryset.model
        except (BaseException) as e:
            raise ValueError("Debe especificar el parámetro 'model' o el parámetro 'queryset' o ambos.")
        self.SetModel(model, queryset)


    def __str__(self):
        return str(self._name) or getattr(self.model, "_meta.verbose_name_plural", None) or _("Reporte")

    def __iter__(self):
        if (self.paginate_by):
            # paginate_queryset(queryset, page_size)
            # Returns a 4-tuple containing (paginator, page, object_list, is_paginated).
            # Constructed by paginating queryset into pages of size page_size. If the request contains a page argument,
            # either as a captured URL argument or as a GET argument, object_list will correspond to the objects from that page.
            try:
                paginator, page, object_list, is_paginated = self.paginate_queryset(self.get_queryset(), self.paginate_by)
            except (AttributeError):
                object_list = self.queryset
        else:
            object_list = self.get_queryset()

        for m_obj in object_list:
            yield Obj(self, m_obj)

    def __len__(self):
        return len(self.get_queryset())

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except (AttributeError) as e:
            try:
                return object.__getattribute__(self, "_{}".format(name))
            except (AttributeError):
                # Vamos a intentar devolver un valor si el name empieza por Get,
                # supondremos que el resto del texto será uno de los atributos de esta
                # clase 'Reporte'.
                # Ejemplo: 'GetName' lo traduciremos como '_name' o 'name'.
                if len(name) > 3:
                    if name[:3].lower() == "get":
                        name = name[3:].lower()
                        return getattr(self, name)   # ************************ PENDIENTE DE REVISIÓN *********************************************
                raise AttributeError(e)

    def __setattr__(self, key, value):
        key2 = "_{}".format(key)
        if (key2 in self.__dict__.keys()):
            self.__dict__[key2] = value
            return
        self.__dict__[key] = value

    # Métodos del modelo (mejorado).---------------------------
    @classmethod
    def GetImg(self):
        return self.model().GetImg()
    # ---------------------------------------------------------


    # ListViews métodos.---------------------------------------
    def get_queryset(self):
        """Método de la clase View desde Django."""
        qs = super().get_queryset()

        request = getattr(self, "request", None)
        if (request):
            q = request.GET.get("q") or None
            field = self.request.GET.get("field")
            paginate_by = self.request.GET.get("limit") or self.request.GET.get("paginate_by") or self.paginate_by

            if (q) and (field) and (field != "tags"):
                qs = qs.filter(**{"%s__icontains" % field: self.GetTag(q, False)})
            elif (q):
                qs = qs.filter(tags__icontains=self.GetTag(q, False))
            self.paginate_by = paginate_by

        self.queryset = qs
        return qs

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reporte"] = self
        context["subtitle"] = self._name
        context["img"] = getattr(self.model, "GetImg", None) or IMG_LIST
        return context


    # --------------------------------------------------------


    def HasEncabezado(self):
        return self._has_encabezado

    def GetModel(self):
        return self.model

    def GetFields(self):
        """
        Obtiene una lista con los campos de este reporte.
        """
        fields = []
        for (key, value) in self.__dict__.items():
            if (not isinstance(value, Field)):
                continue
            if (key == "img"): # La imagen siempre irá al principio.
                fields.insert(0, value)
            else:
                fields.append(value)
        return fields

    def SetRowCssClass(self, name):
        self._rowcssclass = name

    def SetName(self, value):
        self.__dict__["_name"] == str(value)

    def SetDescription(self, value):
        self.__dict__["__description"] = str(value)

    def SetModel(self, value, queryset=None):
        self.__dict__["model"] = value
        if queryset is None:
            self.__dict__["queryset"] = value.objects.all()
        else:
            self.__dict__["queryset"] = queryset

    def SetQueryset(self, queryset):
        self.__dict__["queryset"] = queryset

    def SetField(self, attrname, name="", verbose_name=None, datatype=STR, cssclass="left", colspan=1):
        if (not name):
            name = attrname
        if (verbose_name == None):
            verbose_name = name.title()
        field = Field(parent=self, name=name, verbose_name=verbose_name, datatype=datatype, cssclass=cssclass, colspan=colspan)
        setattr(self, name.lower(), field)
        self._fields[name] = attrname

    def SetFieldsDefault(self, include_parents=False, include_hidden=False):
        """
        Establece las fields predeterminadas del modelo.
        Útil para cuando no se declara ninguna field.
        """
        # La imagen del objeto en la primera columna (si tiene).
        if hasattr(self.model, "GetImg"):
            self.SetField(attrname="img", name="GetImg", verbose_name="", datatype=HTML_IMAGE)

        for mf in self.model._meta.get_fields(include_parents=include_parents, include_hidden=include_hidden):
            tipo = STR
            name = mf.name
            if name in ("tags",):
                continue
            if isinstance(mf, (models.CharField, models.TextField)):
                tipo = STR
            elif isinstance(mf, (models.IntegerField, models.BigIntegerField, models.BigAutoField, models.AutoField)):
                tipo = INT
            elif isinstance(mf, (models.DecimalField,)):
                tipo = DECIMAL
            elif isinstance(mf, (models.FloatField,)):
                tipo = FLOAT
            elif isinstance(mf, (models.DateField,)):
                tipo = DATE
            elif isinstance(mf, (models.DateTimeField,)):
                tipo = DATETIME
            elif isinstance(mf, (models.ForeignKey, models.ManyToManyField)):
                tipo = STR
                name = "%s" % mf.name
            else:
                continue
            if getattr(mf, "verbose_name", None):
                verbose_name = mf.verbose_name
            else:
                verbose_name = mf.name.title()
            self.SetField(name, name, verbose_name, tipo)

    def SetTotalesFields(self, *fields):
        for field in fields:
            self._totales_fields.append(field)

    def __sumar(self, x, y):
        return x + y

    def GetTotal(self, field):
        """
        Obtiene la sumatoria de la field indicada en cada objeto...
        Si se especifica un método, también funcionará.
        """
        out = 0
        for obj in self:
            out += getattr(obj, field.name)
        return out

    def GetTotales(self):
        """
        Obtiene un diccionario con los totales de 
        la suma de todos los objetos.
        """
        out = {}
        for field in self._totales_fields:
            out[field.verbose_name] = self.GetTotal(field)
        return out

    def GetTotalesForTable(self):
        """
        Obtiene una lista de diccionarios con los totales para las fields indicadas,
        Igual que GetTotales a diferencia que la lista tendrá elementos vacios... de
        modo que coincidan con el número de fields que se mostrará en el listado, quedando
        cada total debajo en su respectiva columna.
        """
        out = []
        totales = self.GetTotales()
        for field in self.GetFields():
            out.append({"field": field, "total": totales.get(field.verbose_name, "")})
        return out




