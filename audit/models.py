
from django.db import models
from simple_history import register

from user.models import User
from company.models import Company
from warehouse.models import Warehouse




# https://django-simple-history.readthedocs.io/en/latest/quick_start.html
# Si desea separar las migraciones del modelo histórico en una aplicación que 
# no sea la aplicación del modelo de terceros, puede configurar el appparámetro 
# en register. Por ejemplo, si desea que las migraciones residan en la carpeta 
# de migraciones del paquete en el que registra el modelo, puede hacer lo 
# siguiente: register(User, app=__package__).

register(User, app=__package__)
register(Company, app=__package__)
register(Warehouse, app=__package__)