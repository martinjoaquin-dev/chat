#!/usr/bin/env python3
"""
Ventana principal de la aplicación con interfaz gráfica.
Permite elegir entre Chat Seguro o Servidor de Archivos.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Chat Seguro con Firma Digital")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.center_window()
        
        # Variables para procesos
        self.server_process = None
        self.file_server_process = None
        
        self.create_widgets()
    
    def center_window(self):
        """Centra la ventana en la pantalla."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Crea los widgets de la interfaz."""
        # Título
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🔐 Sistema de Chat Seguro con Firma Digital",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=25)
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#ecf0f1", padx=40, pady=40)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Descripción
        desc_label = tk.Label(
            main_frame,
            text="Selecciona el servicio que deseas usar:",
            font=("Arial", 12),
            bg="#ecf0f1",
            fg="#34495e"
        )
        desc_label.pack(pady=(0, 30))
        
        # Botón Chat Seguro
        chat_btn = tk.Button(
            main_frame,
            text="💬 Chat Seguro",
            font=("Arial", 14, "bold"),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=30,
            pady=15,
            command=self.open_chat_window
        )
        chat_btn.pack(pady=10, fill=tk.X)
        
        # Botón Servidor de Archivos
        files_btn = tk.Button(
            main_frame,
            text="📁 Servidor de Archivos y Firma Digital",
            font=("Arial", 14, "bold"),
            bg="#27ae60",
            fg="white",
            activebackground="#229954",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=30,
            pady=15,
            command=self.open_files_window
        )
        files_btn.pack(pady=10, fill=tk.X)
        
        # Botón Salir
        exit_btn = tk.Button(
            main_frame,
            text="Salir",
            font=("Arial", 10),
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8,
            command=self.on_closing
        )
        exit_btn.pack(pady=(20, 0))
        
        # Footer
        footer_label = tk.Label(
            self.root,
            text="Versión 6.0 | Sistema de Comunicación Segura",
            font=("Arial", 8),
            bg="#ecf0f1",
            fg="#7f8c8d"
        )
        footer_label.pack(side=tk.BOTTOM, pady=10)
    
    def open_chat_window(self):
        """Abre la ventana del chat."""
        self.root.withdraw()
        chat_window = tk.Toplevel()
        from gui.chat_window import ChatWindow
        ChatWindow(chat_window, self)
    
    def open_files_window(self):
        """Abre la ventana del servidor de archivos."""
        self.root.withdraw()
        files_window = tk.Toplevel()
        from gui.files_window import FilesWindow
        FilesWindow(files_window, self)
    
    def show_main(self):
        """Muestra la ventana principal."""
        self.root.deiconify()
    
    def on_closing(self):
        """Maneja el cierre de la aplicación."""
        if messagebox.askokcancel("Salir", "¿Deseas salir de la aplicación?"):
            # Cerrar procesos si están corriendo
            if self.server_process:
                self.server_process.terminate()
            if self.file_server_process:
                self.file_server_process.terminate()
            self.root.destroy()

def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()

