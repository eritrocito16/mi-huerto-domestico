import os
import unicodedata
import re

# Ruta real desde la carpeta donde está manage.py
carpeta = 'huerto_app/static/img/plantas/'

def slugify(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^a-zA-Z0-9\s-]', '', value).strip().lower()
    return re.sub(r'[\s\-]+', '-', value)

for nombre in os.listdir(carpeta):
    ruta_original = os.path.join(carpeta, nombre)

    if nombre.lower().endswith(('.jpg', '.jpeg')):
        nombre_base = os.path.splitext(nombre)[0]
        nuevo_nombre = slugify(nombre_base) + '.jpeg'
        nueva_ruta = os.path.join(carpeta, nuevo_nombre)

        print(f'Renombrando: {nombre} → {nuevo_nombre}')
        os.rename(ruta_original, nueva_ruta)

print("✅ Imágenes renombradas exitosamente.")
