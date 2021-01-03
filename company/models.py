

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l
from django.urls import reverse_lazy

from unoletutils.libs import utils



class Company(models.Model, utils.ModelBase):
    """
    Representa una empresa en la base de datos.

    Una empresa es una entidad que pertenece a un site y puede contener varios
    almacenes. Entonces las empresas tendrían el 2do nivel de prioridad después
    de los sites.
    """

    site = models.ForeignKey(Site, on_delete=models.PROTECT, editable=False)

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    admin_users = models.ManyToManyField(settings.AUTH_USER_MODEL, 
    related_name="admin_users_company_set", blank=True)

    name = models.CharField(_l("nombre"), max_length=100,
    help_text=_l("nombre de la empresa para el público."))

    business_name = models.CharField(_l("Razón social"), max_length=100,
    help_text=_l("nombre legal registrado de la empresa."))

    is_active = models.BooleanField(_l("activo"), default=True)

    create_user = models.ForeignKey(settings.AUTH_USER_MODEL, 
    related_name="create_user_company_set", on_delete=models.PROTECT, null=True, 
    blank=True, editable=True)

    create_date = models.DateTimeField(auto_now_add=True, null=True, 
    blank=True, editable=False)

    objects = models.Manager()

    on_site = CurrentSiteManager()

    class Meta:
        verbose_name = _l("empresa")
        verbose_name_plural = _l("empresas")
        ordering = ["site", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy("company-company-detail", kwargs={"company": self.pk})

    def clean(self):
        if not self.pk:
            self.site = Site.objects.get_current()
        
    def user_has_access(self, user) -> bool:
        """Comprueba si el usuario tiene acceso a esta empresa."""
        if (user in self.users.all()) or (user in self.admin_users.all()):
            return True
        return False

    def user_is_admin(self, user) -> bool:
        """Comprueba si el usuario es administrador en esta empresa."""
        if (user in self.admin_users.all()):
            return True
        return False
    
    def user_is_simple(self, user) -> bool:
        """Comprueba si el usuario tiene acceso pero no es administrador."""
        if (user in self.users.all()) and (not user in self.admin_users.all()):
            return True
        return False

    def get_user_list(self, is_active=True):
        """Obtiene todos los usuarios que tinen acceso a esta empresa."""
        qs = self.admin_users.all() | self.users.all()
        return qs.filter(is_active=is_active)

    def get_warehouse_list(self, is_active=True):
        """Obtiene los almacenes de esta empresa."""
        return self.warehouse_set.filter(is_active=is_active)

    def has_warehouse(self, warehouse):
        """Comprueba si el almacén activo pertenece a esta empresa."""
        if warehouse in self.get_warehouse_list():
            return True
        return False

    

