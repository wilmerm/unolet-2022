"""
Paquete 'fuente' es el núcleo de todas las operaciones de Unolet.

Modules:

    csv: manejo de archivo con formato csv, haciendo uso de la librería csv.

    detail: para mostrar detalles de instancias de modelos Django.

    email: para enviar y recibir mails.

    encriptado: trabaja con encriptación.

    exceptions: todas las excepciones predefinidas del proyecto.

    fecha: trabajar con fechas.

    grafico: trabajar con gráficos estadísticos.

    html: etiquetas html represendas como objetos Python.

    icons: ofrece acceso a las imágenes del directorio static de esta app.

    json: trabaja con objetos en formato json.

    mobile: funciones útiles para dispositivos móviles.

    number: trabaja con números y tipos numéricos Python.

    numero_letras: trabaja con representación textual de números.

    paises: funciones e informaciones útiles de paises.

    pdf: crea documentos en pdf.

    prestamo: funciones útiles para cálculos de préstamos personales.

    report: generación de reportes.

    reporte: **Deprecation**

    text: funciones útiles para trabajar con textos.

    utils: varias funciones y clases útiles.

    var: todas las constantes globales del proyecto.

"""

import warnings


# warnings — Warning control
# https://docs.python.org/2/library/warnings.html

# https://docs.python.org/2/library/warnings.html#the-warnings-filter
# "error": turn matching warnings into exceptions
# "ignore": never print matching warnings
# "always": always print matching warnings
# "default": print the first occurrence of matching warnings for each location where the warning is issued
# "module": print the first occurrence of matching warnings for each module where the warning is issued
# "once": print only the first occurrence of matching warnings, regardless of location

warnings.simplefilter('default', DeprecationWarning)