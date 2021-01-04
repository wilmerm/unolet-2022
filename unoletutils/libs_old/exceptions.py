"""
Errores predefinidos de Unolet.
"""
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.http import HttpRequest
import sys


class Error(Exception):
    """
    Exception base para el resto de las excepciones del paquete.
    """

class ReportError(Error):
    """Error en un reporte."""


class FieldError(Error):
    """Error en campo de un reporte."""


class TextError(Error):
    """Error en el módulo text."""


class Log:
    """
    Esta clase almacena todo lo que capturemos con fuente.exceptions.Log(texto).

    El log permanecerá en la instancia ejecutandose actualmente, hasta que sea
    reiniciado el servidor.

    Esta clase será útil para capturar eventos que, como administrador del
    sistema, queremos visualizar luego para evaluar el comportamiento del mismo.

    Uso:
        from fuente import exceptions

        exceptions.Log('Este texto será almacenado.')

        try:
            int('hola')
        except (ValueError) as e:
            exceptions.Log(e) # se obtendrá información adicional desde el error.

    """
    logs = []

    @classmethod
    def create_item(cls, message, exception=None, request=None):
        """
        Crea un item para añadir al listado.
        """
        if isinstance(message, Exception):
            exception = exception or message
            message = str(message)

        return {"date": timezone.now(), "message": message,
        "exception": exception, "request": request}

    @classmethod
    def Append(cls, obj, exception=None, request=None):
        item = cls.create_item(obj, exception, request)
        cls.logs.insert(0, item)
        print(item)

    @classmethod
    def Clear(cls, index):
        cls.logs.clear()
