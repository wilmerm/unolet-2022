"""
Módulo para obtener iconos en formato .svg desde el directorio static de la app.

"""
from pathlib import Path
from django.conf import settings




ICON_DIR = Path(__file__).resolve().parent / 'static/icons'
STATIC_URL = settings.STATIC_URL




def get_url(name: str, override: bool=True) -> str:
    """
    Obtiene la url definitiva para el archivo SVG que coincida con el nombre.

    Si override es False, se lanzará una excepción en caso de no encontrar el 
    archivo con el nombre indicado.

    """
    override = bool(override)

    if override is False:
        open(ICON_DIR / name, "r") # Lanzará una excepción si no se encuentra.

    return STATIC_URL + name
    




def get_data(name: str, override: bool=True) -> str:
    """
    Obtiene el contenido del archivo SVG que coincida con el nombre.

    Si override es False, se lanzará una excepción en caso de no encontrar el 
    archivo con el nombre indicado.
    
    """
    override = bool(override)

    if override is False:
        return open(ICON_DIR / name, "r").read() # Lanzará una excepción...

    try:
        return open(ICON_DIR / name, "r").read()
    except (OSError):
        return ""
