# unolet-2022
Unolet Sistema Contable 2022 (proyecto previsto para el año 2022).

## author
Wilmer Martinez <wilmermorelmartinez@gmail.com>


## Dependencias
* pillow
* django-unoletutils
* django-simple-history https://django-simple-history.readthedocs.io/
* django-bootstrap4


## Estructura de las urls
Por nivel de prioridad las urls tendrán esta estructura:
dominio.com/(company.pk)/(warehouse.pk)/...

Cada sitio contendrá una o varias empresas.
Cada empresa contendrá uno o varios almacenes.
Cada empresa contendrá sus propios artículos.

site.
    company.
        warehouse.
        item




Cada grupo pertenecerá a una empresa.
Y en la vista se determinará si dicho usuario está incluido en algun grupo de la empresa,
y si dicho grupo tiene los permisos requeridos.
