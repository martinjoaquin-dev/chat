#!/usr/bin/env python3
"""
Script simple para verificar la firma de un archivo.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8080"

def verificar_firma(filename):
    """Verifica la firma de un archivo."""
    print(f"Verificando firma de: {filename}")
    
    data = {'filename': filename}
    
    response = requests.post(
        f"{BASE_URL}/verify",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get('signature_valid'):
            print("\n[OK] Firma VALIDA")
            print("El archivo NO ha sido modificado desde que se firmo")
            print(f"Verificado en: {result['verified_at']}")
            return True
        else:
            print("\n[ERROR] Firma INVALIDA")
            print("El archivo FUE MODIFICADO despues de firmarse")
            print(f"Verificado en: {result['verified_at']}")
            return False
    else:
        print(f"\n[ERROR] Error al verificar: {response.status_code}")
        print(response.text)
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python verificar_firma.py <nombre_archivo>")
        print("Ejemplo: python verificar_firma.py documento.txt")
        sys.exit(1)
    
    filename = sys.argv[1]
    verificar_firma(filename)

