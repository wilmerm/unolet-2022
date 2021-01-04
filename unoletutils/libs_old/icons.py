"""
Módulo para obtener iconos en formato .svg desde el directorio static de la app.

"""
import datetime
import re
from pathlib import Path
from django.conf import settings



ICON_DIR = Path(__file__).resolve().parent.parent / 'static/icons'
STATIC_URL = settings.STATIC_URL



def get_url(name: str, override: bool=True) -> str:
    """
    Obtiene la url definitiva para el archivo SVG que coincida con el nombre.

    Si override es False, se lanzará una excepción en caso de no encontrar el 
    archivo con el nombre indicado.

    """
    if not ".svg" in name:
        name += ".svg"

    override = bool(override)

    if override is False:
        open(ICON_DIR / name, "r") # Lanzará una excepción si no se encuentra.

    return STATIC_URL + "icons/" + name
    

def get_data(name: str, override: bool=True) -> str:
    """
    Obtiene el contenido del archivo SVG que coincida con el nombre.

    Si override es False, se lanzará una excepción en caso de no encontrar el 
    archivo con el nombre indicado.
    
    """
    if not ".svg" in name:
        name += ".svg"

    override = bool(override)

    if override is False:
        return open(ICON_DIR / name, "r").read() # Lanzará una excepción...

    try:
        return open(ICON_DIR / name, "r").read()
    except (OSError):
        return ""


def svg(name: str, size: str=None, fill: str=None, id: str=None) -> dict:
    """
    Retorna el contenido del archivo SVG con el nombre indicado.

    Nota: retorna el contenido, no la ruta, en un archivo .SVG.

    Parameters:
        filename (str): Nombre del archivo o ruta. Si se indica el nombre del 
        archivo, buscará dentro de los directorios static/img/* predeterminados.
        Si se indica una ruta, tendrá que empezar por /static/*

        size (str): El size se pasará a las opciones CSS (width, height) tal y 
        como se especifiquen, por lo cual es conveniente indicar su tipo de 
        medida (ejemplos '32px', '2rem', etc.).

        fill (str): CSS color que se pasará a la opción fill para pintar la 
        imagen.

    """
    fill = fill or 'var(--secondary)'

    try:
        svg = get_data(name, override=False)
    except (BaseException):
        return {"svg": "", "size": size, "fill": fill, "name": name, "id": id}

    # Eliminamos los saltos de línea y espacios extras.
    svg = " ".join(svg.replace("\n", " ").split())

    # if not id:
    #     id = f"id-svg-{name}-fill-{fill}-size-{size}-{datetime.datetime.today()}"
    #     id = text.Text.FormatCodename(id)

    if size in ("", "none", "null", "auto"):
        if (" width=" in svg):
            svg = re.sub(r'\swidth=(["\']).*?["\']\s', '', svg, count=1)
        
        if (" height=" in svg):
            svg = re.sub(r'\sheight=(["\']).*?["\']\s', '', svg, count=1)

    elif size:
        if (not " width=" in svg):
            svg = re.sub(r'<svg\s', f'<svg width="{size}" ', svg, count=1)
        else:
            svg = re.sub(r'\swidth=(["\']).*?["\']\s', f' width="{size}" ', 
            svg, count=1)
    
        if (not " height=" in svg):
            svg = re.sub(r'<svg\s', f'<svg height="{size}" ', svg, count=1)
        else:
            svg = re.sub(r'\sheight=(["\']).*?["\']\s', f' height="{size}" ', 
            svg, count=1)

    if (not " fill=" in svg):
        svg = re.sub(r'<svg\s', f'<svg fill="{fill}" ', svg, count=1)
    else:
        svg = re.sub(r'\sfill=(["\']).*?["\']\s', f' fill="{fill}" ', svg, 
        count=1)

    return {"svg": svg, "size": size, "fill": fill, "name": name, "id": id}