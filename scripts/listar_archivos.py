#!/usr/bin/env python3
"""
Script simple para listar archivos subidos.
"""

import requests
import json

BASE_URL = "http://localhost:8080"

def listar_archivos():
    """Lista todos los archivos subidos."""
    print("Listando archivos subidos...\n")
    
    response = requests.get(f"{BASE_URL}/files")
    
    if response.status_code == 200:
        result = response.json()
        files = result.get('files', [])
        
        if not files:
            print("No hay archivos subidos")
        else:
            print(f"Total de archivos: {len(files)}\n")
            print(f"{'Archivo':<30} {'Tamaño':<15} {'Fecha':<25}")
            print("-" * 70)
            
            for file_info in files:
                filename = file_info['filename']
                size = file_info['size']
                uploaded_at = file_info['uploaded_at']
                
                # Formatear tamaño
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.2f} KB"
                else:
                    size_str = f"{size / (1024 * 1024):.2f} MB"
                
                print(f"{filename:<30} {size_str:<15} {uploaded_at:<25}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == '__main__':
    listar_archivos()

