"""
Script para calcular MD5 de archivos .py del proyecto.
"""

import hashlib
import os
from datetime import datetime

def calcular_md5(archivo):
    """Calcula el MD5 de un archivo."""
    hash_md5 = hashlib.md5()
    try:
        with open(archivo, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        return f"ERROR: {e}"

def obtener_md5_archivos():
    """Obtiene MD5 de todos los archivos .py en el directorio actual."""
    archivos_py = []
    for archivo in os.listdir('.'):
        if archivo.endswith('.py') and os.path.isfile(archivo):
            md5 = calcular_md5(archivo)
            fecha = datetime.fromtimestamp(os.path.getmtime(archivo)).strftime('%Y-%m-%d')
            archivos_py.append((archivo, md5, fecha))
    
    return sorted(archivos_py)

if __name__ == '__main__':
    print("=== CÁLCULO DE MD5 DE ARCHIVOS .PY ===\n")
    archivos = obtener_md5_archivos()
    
    print("Archivo | MD5 | Fecha de modificación")
    print("-" * 80)
    for archivo, md5, fecha in archivos:
        print(f"{archivo:30} | {md5:32} | {fecha}")
    
    print("\n=== FORMATO PARA CONTROL DE CAMBIOS ===")
    print("\n| Archivo | MD5 | Fecha de cambio |")
    print("|---------|-----|------------------|")
    for archivo, md5, fecha in archivos:
        print(f"| {archivo} | `{md5}` | {fecha} |")

