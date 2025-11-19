#!/usr/bin/env python3
"""
Script simple para subir y firmar un archivo.
"""

import requests
import json
import sys
import os

BASE_URL = "http://localhost:8080"

def subir_archivo(file_path):
    """Sube y firma un archivo."""
    if not os.path.exists(file_path):
        print(f"Error: Archivo {file_path} no existe")
        return None
    
    print(f"Subiendo archivo: {file_path}")
    
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n[OK] Archivo subido y firmado exitosamente!")
        print(f"Archivo: {result['filename']}")
        print(f"Tamaño: {result['size']} bytes")
        print(f"Firma guardada en: {result['signature_path']}")
        print(f"Hash SHA256: {result['signature']['hash']}")
        return result['filename']
    else:
        print(f"\n[ERROR] Error al subir archivo: {response.status_code}")
        print(response.text)
        return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python subir_archivo.py <ruta_al_archivo>")
        print("Ejemplo: python subir_archivo.py documento.txt")
        sys.exit(1)
    
    file_path = sys.argv[1]
    filename = subir_archivo(file_path)
    
    if filename:
        print(f"\nPara verificar la firma, ejecuta:")
        print(f"python verificar_firma.py {filename}")

