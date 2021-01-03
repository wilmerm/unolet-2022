from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth.models import (AbstractUser, AbstractBaseUser, 
    PermissionsMixin, Group)
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import Permission

from unoletutils.libs import utils, icons


Group.add_to_class("site", models.ForeignKey(Site, on_delete=models.CASCADE, 
    blank=True, null=True))


class User(AbstractUser, utils.ModelBase):
    """
    Representa un usuario en la base de datos. 
    
    Este modelo reemplaza el modelo User default de django. Se hará referencia 
    a él mediante la variable AUTH_USER_MODEL del 'settings'. Ejemplo:

        user = models.ForeignKey(settings.AUTH_USER_MODEL).

    Debe establecer la variable 'AUTH_USER_MODEL' en el 'setting'
    de la siguiente manera:

        AUTH_USER_MODEL = 'user.User'
    """

    # Site al que pertenece el usuario.
    site = models.ForeignKey(Site, on_delete=models.PROTECT, blank=True, 
    null=True, editable=False)

    # Usado para solicitar al usuario que cambie su contraseña.
    request_change_password = models.BooleanField(default=False)


    class Meta:
        verbose_name = _l("usuario")
        verbose_name_plural = _l("usuarios")
        ordering = ["-is_active", "is_superuser", "is_staff", "username"]
        permissions = (
            # Permiso para que el personal administrativo de la empresa,
            # pueda entrar al formlario de usuarios y modificar parámetros 
            # específicos de ese usuario. 
            # Por cuestiones de seguridad, los permisos predeterminados 
            # (add, change, delete, view) están reservados solo para el 
            # administrador del sistema.
            ("admin_user", _l("Puede administrar usuarios")),
        )

    def get_absolute_url(self):
        return reverse_lazy("user-user-update", kwargs={"pk": self.pk})

    def get_user_permissions(self):
        """
        Obtiene todos los permisos de este usuario. Ya sea asignados 
        directamente o a traves de los grupos que pertenece.
        """
        return self.user_permissions.all() | Permission.objects.filter(
            group__user=self)

    @classmethod
    def get_img(cls):
        """Obtiene la url de un ícono svg que representa un usuario."""
        return icons.get_url("person-fill")

    def get_companies(self):
        """Obtiene las empresas que este usuario tiene accesso."""
        return self.company_set.all() | self.admin_users_company_set.all()


