"""
https://docs.djangoproject.com/en/3.1/topics/http/middleware/
"""
from django.http import HttpResponseNotFound, Http404
from django.utils.deprecation import MiddlewareMixin
from company.models import Company


def get_or_add_company_to_request(request, view_kwargs=None):
    """
    Obtiene la instancia de la empresa actual almacenada en request.company.
    Si no exite, se intentará obtener la instancia de la empresa actual y 
    agregarla al request.company.
    """
    try:
        request.company = getattr(request, "company", 
                Company.objects.get(pk=view_kwargs["company"]))
    except (KeyError):
        request.company = None
    return request.company


class CheckUserInCompanyMiddleware(MiddlewareMixin):
    """
    Middleawre que comprueba si el usuario logueado pertenece a la empresa
    que intenta acceder.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            company = get_or_add_company_to_request(request, view_kwargs)
        except (Company.DoesNotExist) as e:
            raise Http404(e)

        if company:
            if not company.user_has_access(request.user):
                raise Http404(
                    f"El usuario {request.user} no pertenece a {company}")

        return None


class CompanyMiddleware(MiddlewareMixin):
    """
    Middleware que agrega la instancia company actual al context y al request.
    {{ request.company }} y {{ company }}.
    """
        
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        process_view() se llama justo antes de que Django llame a la vista.

        Parameters:
            request: HttpRequest objeto. 

            view_func: es la función de Python que Django está a punto de usar.
            (Es el objeto de función real, no el nombre de la función).

            view_args: lista de argumentos posicionales que se pasarán a la 
            vista.

            view_kwargs: diccionario de argumentos de palabras clave que se 
            pasarán a la vista. 
        """
        get_or_add_company_to_request(request, view_kwargs)

    def process_template_response(self, request, response):
        response.context_data["company"] = request.company
        return response
