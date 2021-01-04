# unolet-2022
Unolet Sistema Contable 2022 (proyecto previsto para el año 2022).

## author
Wilmer Martinez <wilmermorelmartinez@gmail.com>


## Dependencias
* pillow
* django-unoletutils
* django-guardian https://django-guardian.readthedocs.io/en/stable/installation.html
* django-simple-history https://django-simple-history.readthedocs.io/
* django-bootstrap4

## Estructura de las urls
Por nivel de prioridad las urls tendrán esta estructura:
dominio.com/<int:company>/...

## Permisos de acceso.
Debido a que un usuario puede tener acceso a varias empresas, pero podría tener
roles diferentes para cada  una, por ejemplo en la empresa A tiene permisos de 
crear documentos pero no de crear artículos, en la empresa B tiene permisos de 
crear artículos, etc. Para eso hacemos uso de django-guardian. De este modo 
asignamos permisos a cada usuario para instancias de empresas de forma 
individual.

https://django-guardian.readthedocs.io/en/stable/installation.html

