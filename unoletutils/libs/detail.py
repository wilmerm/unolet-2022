"""
Detalle para instancias django.models.Model

Con la clase 'Detail' pasándole una instancia de django.db.models.Model,
obtenemos un objeto que será útil para mostrar los datos necesarios del
objeto django.db.models.Model en las plantillas HTML.
"""


from django.db import models
from django.utils.translation import gettext as _

try:
    from user.models import User
except (ImportError):
    pass

from fuente import (var, reporte, json)




class Detail():
    """
    Clase base Detalle.

    Arguments:
    obj -- Una instancía de django.db.models.Model
    """

    def __init__(self, obj, *args, **kwargs):

        if (not isinstance(obj, models.Model)):
            pass # raise TypeError("El argumento 'obj' debe ser una instancia django.db.models.Model. Usted ha indicado un tipo '%s' (%s)." % (type(obj), obj))

        self.__dict__["_obj"] = obj
        self.__dict__["_model"] = obj.__class__

        try:
            self.__dict__["verbose_name"] = kwargs.get("verbose_name") or obj._meta.verbose_name
        except (AttributeError):
            self.__dict__["verbose_name"] = obj.__class__.__name__

        if kwargs.get("set_fields_default"):
            self.SetFieldsDefault()

    def __str__(self):
        if (not self._obj):
            return _("Ninguno")
        return "%s" % self._obj

    def __repr__(self):
        return "<%s '%s'>" % str(self.__class__.__name__, self._obj)

    def __bool__(self):
        return bool(self._obj)

    def __iter__(self):
        for field in self.GetFieldsAndDetails():
            yield field

    def __getattribute__(self, name):
        # Primero buscamos en el objeto actual.
        error = ""

        try:
            return super().__getattribute__(name)
        except (AttributeError) as e:
            error += str(e)
    
        try:
            return getattr(self.__dict__["_obj"], name)
        except (AttributeError) as e:
            raise AttributeError(error + f" {e}")

    def __setattr__(self, name, value):

        # Para atributos recervados.
        if name[0] == "_":
            self.__dict__[name] = value
            return

        # Cuando intentamos establecer otro detalle como atributo.
        if isinstance(value, Detail):
            return object.__setattr__(self, name, value)

        # Cuando intentamos establer directamente una field.
        elif isinstance(value, reporte.Field):
            name = value.name
            field = value

        # Cuando establecemos un nombre y valor, creamos una field.
        else:
            # Si la field esta registrada, solo cambiamos su valor.
            try:
                self.SetFieldValue(name, value)
                return
            except (AttributeError):
                field = reporte.Field(self, name)
                field.SetValue(value)

        obj_attr = None
        
        if obj_attr is None:
            obj_attr = getattr(self._obj, name, field.value)
            try:
                obj_attr = obj_attr()
            except (TypeError):
                pass

        field.SetValue(obj_attr)
        
        return object.__setattr__(self, name, field)

    def is_detail(self):
        return True

    def Exclude(self, *names):
        """
        ::names: nombres de campos que serán excluidos
        de este detalle.
        """
        fields_names = [e.name for e in self.GetFields() if e.name in names]
        for name in fields_names:
            try:
                self.__dict__[name] = None
            except (KeyError):
                pass

    def GetFields(self):
        """Obtiene los atributos de tipo Field."""
        out = []
        if (not self._obj):
            return out
        for item in self.__dict__.items():
            if isinstance(item[1], reporte.Field):
                out.append(item[1])
        return out

    def GetDetails(self):
        """Obtiene los atributos de tipo Detail."""
        out = []
        if (not self._obj):
            return []
        for item in self.__dict__.items():
            if isinstance(item[1], Detail):
                out.append(item[1])
        return out

    def GetFieldsAndDetails(self):
        out = []
        if (not self._obj):
            return out
        for item in self.__dict__.items():
            if isinstance(item[1], (reporte.Field, Detail)):
                out.append(item[1])
        return out

    def GetDict(self):
        """
        Obtiene un diccionario con los nombres de los campos y sus valores.
        """
        out = dict([(e.name, e.value) for e in self.GetFields()])
        return out

    def GetJson(self):
        """
        Retorna este detalle en formato ideal para serializar a JSON.
        """
        return json.clean(self.GetDict())
        
    def GetObject(self):
        return self.__dict__["_obj"]

    def GetModel(self):
        return self.__dict__["_model"]

    def SetValue(self, value):
        """Establece la instancia object Model a este detalle."""
        self.__dict__["_obj"] = value

    def SetField(self, attrname, name=None, verbose_name=None, datatype=var.STR, 
        value=var.UNDEFINED, model_fields=None):
        if (name == None):
            name = attrname

        choices = getattr(model_fields, "choices", None)
        if (choices):
            name = f"get_{name}_display"

        if (verbose_name == None):
            verbose_name = name

        field = reporte.Field(parent=self, name=attrname, 
            verbose_name=verbose_name, datatype=datatype)
        field.SetValue(value)

        return setattr(self, attrname, field)

    def SetFieldValue(self, name, value):
        """Establece el valor a mostrar a una field ya existente."""
        field = getattr(self, name)
        field.SetValue(value)
        return field

    def SetFieldsDefault(self, include_parents=False, include_hidden=False):
        """
        Establece las fields predeterminadas del modelo. 
        
        Util para cuando no se declara ninguna field.
        """
        if (not self._obj):
            return

        try:
            model_fields = self._obj._meta.get_fields(
                include_parents=include_parents, include_hidden=include_hidden)
        except (AttributeError):
            return 

        for mf in model_fields:
            tipo = var.STR
            name = mf.name

            # Si la field no es editable no se incluirá.
            # Estas field se incluyen aunque no sean editables:
            exceptions = ("create_user", "update_user", "create_date", "update_date")
            if ((not getattr(mf, "editable", True)) 
                and (include_hidden == False) and (not name in exceptions)):
                continue

            try:
                verbose_name = mf.verbose_name
            except (AttributeError):
                verbose_name = name.title().replace("_", " ")

            if name in ("id", "tags"):
                continue
            if isinstance(mf, (models.CharField, models.TextField)):
                tipo = var.STR
            elif isinstance(mf, (models.IntegerField, models.BigIntegerField, 
                models.BigAutoField, models.AutoField)):
                tipo = var.INT
            elif isinstance(mf, (models.DecimalField,)):
                tipo = var.DECIMAL
            elif isinstance(mf, (models.FloatField,)):
                tipo = var.FLOAT
            elif isinstance(mf, (models.DateField,)):
                tipo = var.DATE
            elif isinstance(mf, (models.DateTimeField,)):
                tipo = var.DATETIME
            # Si es otro objeto se crea el campo como otro detalle.
            elif isinstance(mf, (models.ForeignKey,)):
                tipo = var.STR
                name = "%s" % mf.name
                obj = getattr(self._obj, name, None)
                if (not isinstance(obj, (User,))):
                    detalle2 = Detail(obj, verbose_name=verbose_name)
                    detalle2.SetFieldsDefault()
                    setattr(self, name, detalle2)
                    continue
            elif isinstance(mf, (models.ManyToManyField,)):
                tipo = var.STR
                name = "%s" % mf.name
            else:
                continue

            self.SetField(attrname=name, name=name, verbose_name=verbose_name, 
                datatype=tipo, model_fields=mf)





