from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l
from django.urls import reverse_lazy
from django.apps import apps
from django.utils.html import format_html

from unoletutils.libs import utils

from module.models import Module


class Company(utils.ModelBase):
    """
    Representa una empresa en la base de datos.

    Una empresa es una entidad que pertenece a un site y puede contener varios
    almacenes. Entonces las empresas tendrían el 2do nivel de prioridad después
    de los sites.
    """

    company = None
    tags = None

    site = models.ForeignKey(Site, on_delete=models.PROTECT, editable=False)

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    admin_users = models.ManyToManyField(settings.AUTH_USER_MODEL, 
    related_name="admin_users_company_set", blank=True)

    name = models.CharField(_l("nombre"), max_length=100,
    help_text=_l("nombre de la empresa para el público."))

    business_name = models.CharField(_l("Razón social"), max_length=100,
    help_text=_l("nombre legal registrado de la empresa."))

    logo = models.ImageField(_l("logo"), blank=True, 
    upload_to=utils.upload_file_on_site)

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

    def save(self, *args, **kwargs):
        if not self.pk:
            # Cuando se registra una nueva empresa, se deberán crear los 
            # permisos de empresa para ella.
            out = super().save(*args, **kwargs)
            CompanyPermission.populate(company=self)
            return out
        return super().save(*args, **kwargs)
        
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

    def get_cascading_modules(self, parent=None):
        out = []
        for obj in Module.objects.filter(parent=parent):
            out.append({
                "name": _(obj.name), 
                "description": _(obj.description),
                "url": obj.build_url(company=self.pk),
                "svg": format_html(obj.get_svg(fill="white")["svg"]),
                "childrens": self.get_cascading_modules(parent=obj),
            })
        return out

    def get_warehouse_list(self, is_active=True):
        """Obtiene los almacenes de esta empresa."""
        return self.warehouse_set.filter(is_active=is_active)

    def has_warehouse(self, warehouse):
        """Comprueba si el almacén activo pertenece a esta empresa."""
        if warehouse in self.get_warehouse_list():
            return True
        return False


class CompanyPermission(utils.ModelBase):
    """
    Permiso dentro de una empresa.

    Este modelo define los permisos personalizados de forma extraordinaria para
    este proyecto. Estos serán asignados a los usuarios por empresa (no global).

    Por ejemplo: El sistema necesita restringir a los usuarios, tal y como se 
    haría utilizando los permisos predeterminados de Django, pero en este caso
    los permisos serán asignados por empresa y no de forma Global. Esto hará 
    que un usuario tenga un permiso determinado en una empresa, pero en otra 
    empresa puede que no lo tenga.

    Estos permisos no serán gestionados por Django, sino que el sistema en si
    contará con su propio sistema de validación de permisos.

    Esto tampoco afectará los permisos predeterminados de Django, ni tampoco 
    afectará la forma de acceder al panel de administración de Django.

    ¿Cómo funciona?
    De lo más simple. Se registra el permiso, asignamos el permiso al usuario,
    establecemos el codename del permisos en la vista como permission_required,
    luego se determinará si el usuario pertenece a la empresa que intenta 
    acceder y si dicho usuario tiene asignado el permiso requerido.
    """

    APP_LABELS = (
        ("user", _l("usuario")), 
        ("audit", _l("auditoría")), 
        ("company", _l("empresa")), 
        ("warehouse", _l("almacén")), 
        ("document", _l("documento")), 
        ("finance", _l("finanzas")),
        ("inventory", _l("inventario")),
        ("person", _l("persona")),
    )

    ACTIONS = (
        ("view", _l("ver")), 
        ("add", _l("agregar")),
        ("change", _l("modificar")),
        ("delete", _l("eliminar"))
    )

    tags = None

    codename = models.CharField(_l("código"), max_length=50, editable=False)

    name = models.CharField(_l("nombre"), max_length=100)

    description = models.CharField(_l("descripción"), max_length=500, blank=True)

    class Meta:
        verbose_name = _l("permiso por empresa")
        verbose_name_plural = _l("permisos por empresa")
        ordering = ["company", "codename", "name"]
        constraints = [
            models.UniqueConstraint(fields=("company", "codename"), 
                name="unique_companypermission_codename"),
            models.UniqueConstraint(fields=("company", "name"), 
                name="unique_companypermission_name"),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        self.codename = self.format_codename(self.codename, allowed="_.")
        self.name = " ".join(self.name.split())
        self.description = " ".join(self.description.split())

    @classmethod
    def populate(cls, company: Company=None, generic_permissions: list=None):
        """
        Registra los permisos para cada empresa registrada, o solo para la 
        empresa indicada.
        """
        if not generic_permissions:
            generic_permissions = []

            for app_label, app_title in cls.APP_LABELS:
                try:
                    models = list(apps.get_app_config(app_label).get_models())
                except (BaseException) as e:
                    raise e.__class__(f"{app_label}. {e}") from e

                for model in models:
                    if "historical" in model._meta.model_name:
                        continue
                    for action, action_title in cls.ACTIONS:
                        codename = f"{app_label}.{action}_{model._meta.model_name}".lower()
                        name = f"{action_title} {model._meta.verbose_name}".title()
                        generic_permissions.append((codename, name))

        if company != None:
            # Se borran los permisos que no estén en generic_permissions. Puede
            # ser que se crearon en un momento, pero ya el modelo o aplicación
            # por la que fueron creados ya no existe.
            db_codenames = CompanyPermission.objects.values_list("codename", flat=True)
            delete_codenames = []
            for db_codename in db_codenames:
                if not db_codename in dict(generic_permissions).keys():
                    delete_codenames.append(db_codename)
            CompanyPermission.objects.filter(codename__in=delete_codenames).delete()

            for codename, name in generic_permissions:
                permission = CompanyPermission(
                    company=company, codename=codename, name=name)
                permission.clean()
                # El permiso se creará solo si no existe.
                try:
                    CompanyPermission.objects.get(company=company, 
                        codename=permission.codename)
                except (CompanyPermission.DoesNotExist):
                    permission.save()
            return
        
        for company in Company.objects.all():
            cls.populate(company, generic_permissions)


class CompanyPermissionGroup(utils.ModelBase):
    """
    Grupos (como los django.auth.Group) pero para CompanyPermission.

    Para trabajar los permisos de acceso por empresa.
    """

    tags = None

    codename = models.CharField(_l("código"), max_length=50)

    name = models.CharField(_l("nombre"), max_length=100)

    permissions = models.ManyToManyField(CompanyPermission, 
    verbose_name=_l("permisos"))

    class Meta:
        verbose_name = _l("grupo de permiso por empresa")
        verbose_name_plural = _l("grupos permisos por empresa")
        ordering = ["company", "codename", "name"]
        constraints = [
            models.UniqueConstraint(fields=("company", "codename"), 
                name="unique_companypermissiongroup_codename"),
            models.UniqueConstraint(fields=("company", "name"), 
                name="unique_companypermissiongroup_name"),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        self.codename = self.format_codename(self.codename, allowed="_")
        self.name = " ".join(self.name.split())