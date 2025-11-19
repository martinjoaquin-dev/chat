#!/usr/bin/env python3
"""
Script principal para ejecutar la aplicación con interfaz gráfica.
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import main

if __name__ == "__main__":
    main()

