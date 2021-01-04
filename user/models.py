from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth.models import AbstractUser, PermissionsMixin, Group
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

    # Permisos por empresa.
    company_permissions = models.ManyToManyField("company.CompanyPermission",
    verbose_name=_l("permisos por empresa"), blank=True)

    # Grupos por empresa.
    company_groups = models.ManyToManyField("company.CompanyPermissionGroup",
    verbose_name=_l("grupo de permisos por empresa"), blank=True)

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
    
    def get_company_permissions(self, company) -> models.QuerySet:
        """Obtiene los permisos de este usuario para la empresa indicada."""
        return self.company_permissions.filter(company=company)

    def get_company_groups(self, company) -> models.QuerySet:
        """Obtiene los grupos de este usuario para la empresa indicada."""
        return self.company_groups.filter(company=company)

    def has_company_permission(self, company, permission) -> bool:
        """
        Comprueba si este usuario tiene el permiso indicado en la empresa.

        Parameters:
            permission (company.models.CompanyPermission or str or iter): 
            permiso que desea comprobar.

            company (company.models.Company): empresa donde se supone que debe
            tener el permiso dicho usuario.

        Notas:
            Aunque el usuario cuente con los permisos, devolverá falso si no 
            pertenece a la empresa en cuestión.

            Los superuser cuentan con todos los permisos, pero igual deben 
            pertenecer a la empresa en cuestión.
        """
        if not company.user_has_access(self):
            return False

        # Pausado mientras se desarrolla...
        #if self.is_superuser:
            #return True

        user_company_permissions = self.get_company_permissions(company)
        if isinstance(permission, str):
            try:
                user_company_permissions.get(codename=permission)
            except (models.ObjectDoesNotExist):
                return False
            return True
        elif isinstance(permission, (tuple, list)):
            for perm in permission:
                if self.has_company_permission(company, perm):
                    return True
            return False

        if permission in user_company_permissions:
            return True
        return False

    def assign_company_permission(self, company_permission, company):
        """
        Asigna al usuario el permiso de empresa para la empresa indicada.

        Parameters:
            company_permission (str or company.models.CompanyPermission or iter):
            Indica el o los permisos que se van a asignar.

            company (company.models.Company): instancia de la empresa donde el 
            usuario usará el o los permisos aquí asignados.
        """
        from company.models import CompanyPermission

        if isinstance(company_permission, str):
            try:
                company_permission = CompanyPermission.objects.get(
                    codename=company_permission, company=company)
            except (models.ObjectDoesNotExist) as e:
                
                permissions_codenames = ", ".join([p.codename for p in 
                    CompanyPermission.objects.filter(company=company)])

                raise models.ObjectDoesNotExist(f"No existe el permiso "
                    f"'{company_permission}' en la empresa '{company}'. {e}.\n"
                    f"-- Permisos: {permissions_codenames}") from e
        
        if isinstance(company_permission, (list, tuple)):
            for item in company_permission:
                self.assign_company_permission(item, company)
            return

        self.company_permissions.add(company_permission)

    @classmethod
    def get_img(cls):
        """Obtiene la url de un ícono svg que representa un usuario."""
        return icons.get_url("person-fill")

    def get_companies(self):
        """Obtiene las empresas que este usuario tiene accesso."""
        return self.company_set.all() | self.admin_users_company_set.all()



