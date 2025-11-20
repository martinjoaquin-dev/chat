#!/usr/bin/env python3
"""
Script interactivo para configurar OAuth 2.0.
Guía al usuario paso a paso para crear credentials.json
"""

import os
import json
from pathlib import Path

def main():
    print("=" * 60)
    print("🔐 CONFIGURACIÓN DE OAUTH 2.0")
    print("=" * 60)
    print()
    
    print("Este script te ayudará a configurar OAuth 2.0 con Google.")
    print()
    
    # Verificar si ya existe
    config_dir = Path("config")
    credentials_file = config_dir / "credentials.json"
    
    if credentials_file.exists():
        print(f"⚠️  Ya existe un archivo: {credentials_file}")
        respuesta = input("¿Deseas reemplazarlo? (s/n): ").lower()
        if respuesta != 's':
            print("Operación cancelada.")
            return
    
    print()
    print("PASO 1: Crear Proyecto en Google Cloud Console")
    print("-" * 60)
    print("1. Ve a: https://console.cloud.google.com/")
    print("2. Inicia sesión con tu cuenta de Google")
    print("3. Crea un nuevo proyecto o selecciona uno existente")
    print()
    input("Presiona Enter cuando hayas creado/seleccionado el proyecto...")
    
    print()
    print("PASO 2: Habilitar API")
    print("-" * 60)
    print("1. En el menú lateral, ve a 'APIs y servicios' → 'Biblioteca'")
    print("2. Busca 'People API' o 'Google+ API'")
    print("3. Haz clic en 'Habilitar'")
    print()
    input("Presiona Enter cuando hayas habilitado la API...")
    
    print()
    print("PASO 3: Crear Credenciales OAuth 2.0")
    print("-" * 60)
    print("1. Ve a 'APIs y servicios' → 'Credenciales'")
    print("2. Haz clic en '+ CREAR CREDENCIALES' → 'ID de cliente de OAuth'")
    print("3. Si es la primera vez, configura la pantalla de consentimiento:")
    print("   - Tipo: Externa")
    print("   - Nombre: Chat Seguro")
    print("   - Email de soporte: Tu email")
    print("   - Continúa hasta 'Volver al panel'")
    print("4. Crea el ID de cliente:")
    print("   - Tipo: Aplicación de escritorio")
    print("   - Nombre: Chat Seguro Desktop")
    print("   - Haz clic en 'Crear'")
    print("5. DESCARGAR JSON (botón 'DESCARGAR JSON')")
    print()
    
    print("PASO 4: Ubicar el archivo descargado")
    print("-" * 60)
    print("El archivo descargado se llamará algo como: client_secret_xxxxx.json")
    print()
    
    archivo_descargado = input("Ingresa la ruta completa del archivo JSON descargado: ").strip()
    
    # Limpiar comillas si las tiene
    archivo_descargado = archivo_descargado.strip('"').strip("'")
    
    if not os.path.exists(archivo_descargado):
        print(f"❌ Error: No se encontró el archivo: {archivo_descargado}")
        return
    
    # Leer el archivo
    try:
        with open(archivo_descargado, 'r', encoding='utf-8') as f:
            datos = json.load(f)
    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
        return
    
    # Verificar formato
    if 'installed' not in datos and 'web' not in datos:
        print("⚠️  Advertencia: El archivo no tiene el formato esperado.")
        print("   Debería tener 'installed' o 'web' como clave principal.")
        respuesta = input("¿Deseas continuar de todos modos? (s/n): ").lower()
        if respuesta != 's':
            return
    
    # Crear directorio config si no existe
    config_dir.mkdir(exist_ok=True)
    
    # Copiar archivo
    try:
        with open(credentials_file, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2)
        print()
        print("✅ ¡Archivo creado exitosamente!")
        print(f"   Ubicación: {credentials_file}")
        print()
        print("PASO 5: Probar la aplicación")
        print("-" * 60)
        print("1. Ejecuta: cd frontend && npm start")
        print("2. Abre http://localhost:4200 en tu navegador")
        print("2. Haz clic en 'Iniciar sesión con Google'")
        print("3. Autoriza la aplicación en el navegador")
        print()
        print("¡Listo! OAuth 2.0 está configurado.")
        
    except Exception as e:
        print(f"❌ Error al crear el archivo: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

