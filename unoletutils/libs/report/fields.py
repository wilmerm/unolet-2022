"""
Campos del reporte.

"""

from decimal import Decimal
import datetime

from django import forms

from fuente import json



class FieldError(Exception):
    """Error para los campos."""




class FieldBase(object):
    """
    Clase base para totos los tipos de campos.
    """
    python_class = object
    form_field_class = None
    form_field_widget_class = forms.TextInput
    form_field_widget_attrs = {}

    def __init__(self, name, verbose_name=None, origen=None, strformat=None,
    cssclass="", jsfunction=None, is_column_total=False):
        self.name = "_".join(name.split())
        self.verbose_name = verbose_name or name.replace("_", " ").title()

        # Especifica el origen de donde se extraerá el valor de este campo.
        # El origen puede ser un campo del modelo en cuestión o un método, etc.
        self.origen = origen

        # Nombres de html clases separadas por espacio que serán aplicadas en 
        # la plantilla.
        self.cssclass = cssclass or ""

        # Es el nombre de una función javascript que queremos aplicar al valor 
        # de este campo. Por ejemplo, si pasamos 'intcomma' como nombre de la 
        # función, en la plantilla se aplicará como: intcomma(value).
        self.jsfunction = jsfunction 

        # Este formato se aplicará en Python con el método str 'format'.
        # aplicándolo al valor. Ej. self.strformat.format(value)
        if strformat:
            self.strformat = "{"+strformat+"}"
        else:
            self.strformat = "{}"

        # Validamos el strformat sea correcto.
        self.format(self.get_value_initial())

        # Esto le informa a la plantilla que este campo deberá sumarse y
        # presentar su total al final de la columna que lo muestra.
        # Esta operación está destinada a que sea javascript quien la ejecute.
        self.is_column_total = bool(is_column_total)

        # Valor lo establecemos al momento de obtener el atributo 
        # __getattribute__ en el objeto fuente.report.base.Item
        self._value = self.get_value_initial()

    def __str__(self):
        return self.format(self.value)

    def get_value_initial(self):
        return self.python_class()

    @property
    def fieldtype(self):
        return self.__class__.__name__

    @property
    def value(self):
        return self._value
            
    @value.setter
    def value(self, value):

        # Tipos de datos str.
        # ----------------------------------------------------------------------
        if (self.python_class == str):
            if value is None:
                value = ""
            if value is False:
                value = _("Si")
            if value is True:
                value = _("No")
        
        # Tipos de datos datetime.
        # ----------------------------------------------------------------------
        if (self.python_class == datetime.datetime):
            if isinstance(value, datetime.datetime):
                self._value = value
            elif isinstance(value, datetime.date):
                self._value = datetime.datetime(value.year, value.month, value.day)
            elif isinstance(value, (list, tuple, set)):
                if len(value < 3) or len(value > 6):
                    raise FieldError(f"Valor {value} inválido para tipo "
                        f"{self.fieldtype}. Si va a especificar un listado debe "
                        f"ser en este orden (mayor a 2) y (menor a 6) " 
                        f"(year, month, day, [hour, [min], [sec]].")
                try:
                    value = [int(e) for e in value]
                except (ValueError):
                    raise FieldError(f"Debe especificar solo números enteros "
                    f"en el listado de valores para tipo {self.fieldtype}, pero "
                    f"se indicó {value}.")

                self._value = self.python_class(*value)

        # Tipos de datos int.
        # ----------------------------------------------------------------------
        elif (self.python_class == int):
            if value in ("", None, False):
                value = 0
            try:
                self._value = self.python_class(value)
            except (ValueError, TypeError) as e:
                raise FieldError(f"El valor '{value}' de tipo {type(value)} no "
                    f"es válido para {self.fieldtype}. {e}")
        
        # Tipos de datos float.
        # ----------------------------------------------------------------------
        elif (self.python_class == float):
            if value in ("", None, False):
                value = float()
            try:
                self._value = self.python_class(value)
            except (ValueError, TypeError) as e:
                raise FieldError(f"El valor '{value}' de tipo {type(value)} no "
                    f"es válido para {self.fieldtype}. {e}")

        # Tipos de datos Decimal.
        # ----------------------------------------------------------------------
        elif (self.python_class == Decimal):
            if value in ("", None, False):
                value = Decimal()
            try:
                self._value = self.python_class(value)
            except (ValueError, TypeError) as e:
                raise FieldError(f"El valor '{value}' de tipo {type(value)} no "
                    f"es válido para {self.fieldtype}. {e}")

        # Cualquier otro tipo de dato no implmentado en validación.
        # ----------------------------------------------------------------------
        else:
            self._value = self.python_class(value)

    def format(self, value):
        """
        Retorna el valor de este campo formateado con self.strformat.

        Returns:
            str: self.strformat.format(value)

        """
        try:
            return self.strformat.format(value)
        except (KeyError) as e:
            raise FieldError(f"Formato inválido '{self.strformat}'.format("
                f"{value}) para {self.fieldtype}. {e}")

    def to_json(self):
        """
        Retorna los atributos de este campo en un diccionario para ser usado 
        en Json.

        name, verbose_name=None, origen=None, strformat=None,
        cssclass="", jsfunction=None

        """
        dic = {
            "name": self.name, 
            "verbose_name": self.verbose_name, 
            "value": self.value, 
            "strvalue": str(self), 
            "origen": self.origen, 
            "strformat": self.strformat, 
            "cssclass": self.cssclass, 
            "jsfunction": self.jsfunction, 
            "is_column_total": self.is_column_total,
        }
        return json.clean(dic)

    def to_python(self, value):
        """
        Retorna el valor de este campo en su correspondiente valor Python.
        """
        return self.python_class(value)



class FieldStrBase(FieldBase):
    """
    Campo base para los campos de tipo texto. (str).
    """
    python_class = str
    form_field_class = forms.CharField

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class FieldNumberBase(FieldBase):
    """
    Campo base para los campos de tipo numérico. (int, float, decimal.Decimal)
    """
    python_class = int
    form_field_class = forms.IntegerField

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __add__(self, other):
        return self.value + getattr(other, "value", other)





class FieldDateBase(FieldBase):
    """
    Campo base para los campos de tipo fecha. (date, datetime).
    """
    python_class = datetime.date
    form_field_class = forms.DateField
    form_field_widget_class = forms.widgets.DateInput
    form_field_widget_attrs = {"type": "date"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_value_initial(self):
        return self.python_class(datetime.MINYEAR, 1, 1)



class CharField(FieldStrBase):
    """
    Campo de texto de longitud variable. (str).
    """
    form_field_class = forms.CharField

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class TextField(FieldStrBase):
    """
    Campo de texto. (str)
    """
    form_field_class = forms.CharField
    form_field_widget_class = forms.widgets.Textarea

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class IntegerField(FieldNumberBase):
    """
    Campo númerico de tipo de valor entero. (int).
    """
    python_class = int
    form_field_class = forms.IntegerField

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class FloatField(FieldNumberBase):
    """
    Campo númerico de tipo de valor en coma flotante. (float)
    """
    python_class = float
    form_field_class = forms.FloatField

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class DecimalField(FieldNumberBase):
    """
    Campo númerico de tipo de valor decimal. (decimal.Decimal)
    """
    python_class = Decimal
    form_field_class = forms.DecimalField

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class DateField(FieldDateBase):
    """
    Campo de fecha de tipo de valor date. (datetime.date)
    """
    python_class = datetime.date
    form_field_class = forms.DateField
    form_field_widget_class = forms.widgets.DateInput

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class DateTimeField(FieldDateBase):
    """
    Campo de fecha de tipo de valor datetime. (datetime.datetime)
    """
    python_class = datetime.datetime
    form_field_class = forms.DateTimeField
    form_field_widget_class = forms.widgets.DateTimeInput

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class BooleanField(FieldBase):
    """
    Campo booleano (True or False).
    """
    python_class = bool
    form_field_class = forms.BooleanField
    form_field_widget_class = forms.widgets.CheckboxInput

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
