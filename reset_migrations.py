"""
Elimina los archivos dentro las carpetas 'migrations'
"""

import os

opt = str(input("Si continua se borrarán todas las migraciones de todas las "
"aplicaciones que se encuentran en el directorio base. Especificamente dentro " 
"de los subdirectorios 'migrations'. ¿Desea continuar? yes/no: "))

if opt.lower() != "yes":
    exit(0)

def removedir(path):
    for name in os.listdir(path):
        p = os.path.join(path, name)
        if os.path.isdir(p):
            removedir(p)
        else:
            try:
                os.remove(p)
            except (WindowsError) as e:
                print(e)
            else:
                print("CORRECTO -- ", p)

path1 = os.curdir

# Remover todos los archivos dentro de los 
# directorios 'migrations' y __pycache__
for dirname in ["migrations", "__pycache__"]:
    for name in os.listdir(path1):
        p = os.path.join(path1, name, dirname)
        if os.path.isdir(p):
            removedir(p)
            try:
                # Volvemos a crear el __init__.py borrado.
                f = open(os.path.join(p, "__init__.py"), "w")
                f.close()
            except (BaseException) as e:
                print(e)
