#!/usr/bin/env python3
"""
Ventana del Servidor de Archivos y Firma Digital con interfaz gráfica.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import requests
import json
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class FilesWindow:
    def __init__(self, root, main_app):
        self.root = root
        self.main_app = main_app
        self.root.title("Servidor de Archivos y Firma Digital")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        self.server_running = False
        self.server_thread = None
        self.base_url = "http://localhost:8080"
        
        self.create_widgets()
        self.center_window()
        
        # Manejar cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Verificar estado del servidor
        self.check_server_status()
    
    def center_window(self):
        """Centra la ventana."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Crea los widgets de la interfaz."""
        # Frame superior - Estado del servidor
        status_frame = tk.Frame(self.root, bg="#34495e", padx=10, pady=10)
        status_frame.pack(fill=tk.X)
        
        self.status_label = tk.Label(
            status_frame,
            text="Servidor: Desconocido",
            font=("Arial", 10, "bold"),
            bg="#34495e",
            fg="#e74c3c"
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.refresh_btn = tk.Button(
            status_frame,
            text="Actualizar",
            font=("Arial", 9),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=3,
            command=self.check_server_status
        )
        self.refresh_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Frame principal con pestañas
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña 1: Subir y Firmar
        upload_frame = tk.Frame(notebook, bg="#ecf0f1")
        notebook.add(upload_frame, text="Subir y Firmar Archivo")
        self.create_upload_tab(upload_frame)
        
        # Pestaña 2: Verificar Firma
        verify_frame = tk.Frame(notebook, bg="#ecf0f1")
        notebook.add(verify_frame, text="Verificar Firma")
        self.create_verify_tab(verify_frame)
        
        # Pestaña 3: Listar Archivos
        list_frame = tk.Frame(notebook, bg="#ecf0f1")
        notebook.add(list_frame, text="Archivos Subidos")
        self.create_list_tab(list_frame)
        
        # Botón volver
        back_btn = tk.Button(
            self.root,
            text="← Volver al Menú Principal",
            font=("Arial", 9),
            bg="#95a5a6",
            fg="white",
            activebackground="#7f8c8d",
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=5,
            command=self.go_back
        )
        back_btn.pack(side=tk.BOTTOM, pady=5)
    
    def create_upload_tab(self, parent):
        """Crea la pestaña de subir archivos."""
        # Frame de selección
        select_frame = tk.Frame(parent, bg="#ecf0f1", padx=20, pady=20)
        select_frame.pack(fill=tk.X)
        
        tk.Label(
            select_frame,
            text="Selecciona un archivo para subir y firmar:",
            font=("Arial", 11, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(anchor=tk.W, pady=(0, 10))
        
        file_frame = tk.Frame(select_frame, bg="#ecf0f1")
        file_frame.pack(fill=tk.X)
        
        self.file_path_var = tk.StringVar()
        self.file_entry = tk.Entry(
            file_frame,
            textvariable=self.file_path_var,
            font=("Arial", 10),
            bg="white",
            fg="#2c3e50",
            state=tk.DISABLED
        )
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(
            file_frame,
            text="Buscar...",
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=5,
            command=self.browse_file
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # Botón subir
        upload_btn = tk.Button(
            select_frame,
            text="Subir y Firmar",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            activebackground="#229954",
            relief=tk.FLAT,
            cursor="hand2",
            padx=30,
            pady=10,
            command=self.upload_file
        )
        upload_btn.pack(pady=(15, 0))
        
        # Área de resultados
        result_frame = tk.Frame(parent, bg="#ecf0f1", padx=20, pady=20)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            result_frame,
            text="Resultado:",
            font=("Arial", 11, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.upload_result = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="white",
            fg="#2c3e50",
            height=10,
            state=tk.DISABLED
        )
        self.upload_result.pack(fill=tk.BOTH, expand=True)
    
    def create_verify_tab(self, parent):
        """Crea la pestaña de verificar firmas."""
        # Frame de selección
        select_frame = tk.Frame(parent, bg="#ecf0f1", padx=20, pady=20)
        select_frame.pack(fill=tk.X)
        
        tk.Label(
            select_frame,
            text="Selecciona un archivo para verificar su firma:",
            font=("Arial", 11, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Lista de archivos
        list_frame = tk.Frame(select_frame, bg="#ecf0f1")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            list_frame,
            text="Archivos disponibles:",
            font=("Arial", 10),
            bg="#ecf0f1",
            fg="#34495e"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.files_listbox = tk.Listbox(
            list_frame,
            font=("Arial", 10),
            bg="white",
            fg="#2c3e50",
            height=8
        )
        self.files_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Botón verificar
        verify_btn = tk.Button(
            select_frame,
            text="Verificar Firma",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            relief=tk.FLAT,
            cursor="hand2",
            padx=30,
            pady=10,
            command=self.verify_file
        )
        verify_btn.pack()
        
        # Área de resultados
        result_frame = tk.Frame(parent, bg="#ecf0f1", padx=20, pady=20)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            result_frame,
            text="Resultado de verificación:",
            font=("Arial", 11, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.verify_result = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="white",
            fg="#2c3e50",
            height=8,
            state=tk.DISABLED
        )
        self.verify_result.pack(fill=tk.BOTH, expand=True)
        
        # Cargar lista de archivos
        self.load_files_list()
    
    def create_list_tab(self, parent):
        """Crea la pestaña de listar archivos."""
        # Frame de controles
        controls_frame = tk.Frame(parent, bg="#ecf0f1", padx=20, pady=20)
        controls_frame.pack(fill=tk.X)
        
        refresh_btn = tk.Button(
            controls_frame,
            text="Actualizar Lista",
            font=("Arial", 10, "bold"),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8,
            command=self.load_files_list
        )
        refresh_btn.pack(side=tk.LEFT)
        
        # Área de lista
        list_frame = tk.Frame(parent, bg="#ecf0f1", padx=20, pady=20)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.files_display = scrolledtext.ScrolledText(
            list_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="white",
            fg="#2c3e50",
            state=tk.DISABLED
        )
        self.files_display.pack(fill=tk.BOTH, expand=True)
    
    def browse_file(self):
        """Abre diálogo para seleccionar archivo."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo para firmar",
            filetypes=[
                ("Todos los archivos", "*.*"),
                ("Archivos de texto", "*.txt"),
                ("Archivos PDF", "*.pdf"),
                ("Archivos ZIP", "*.zip")
            ]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
    
    def upload_file(self):
        """Sube y firma un archivo."""
        file_path = self.file_path_var.get()
        
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Por favor selecciona un archivo válido.")
            return
        
        # Verificar extensión
        ext = Path(file_path).suffix.lower()
        if ext not in ['.txt', '.pdf', '.zip']:
            messagebox.showwarning(
                "Advertencia",
                f"Extensión {ext} puede no ser soportada.\nSoportadas: .txt, .pdf, .zip"
            )
        
        self.upload_result.config(state=tk.NORMAL)
        self.upload_result.delete(1.0, tk.END)
        self.upload_result.insert(tk.END, "Subiendo archivo...\n")
        self.upload_result.config(state=tk.DISABLED)
        
        def upload_thread():
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
                    response = requests.post(f"{self.base_url}/upload", files=files, timeout=30)
                
                result = response.json()
                
                self.root.after(0, lambda: self.show_upload_result(result, response.status_code))
                
            except requests.exceptions.ConnectionError:
                self.root.after(0, lambda: self.show_error("No se pudo conectar al servidor. ¿Está corriendo?"))
            except Exception as e:
                self.root.after(0, lambda: self.show_error(f"Error: {str(e)}"))
        
        threading.Thread(target=upload_thread, daemon=True).start()
    
    def show_upload_result(self, result, status_code):
        """Muestra el resultado de la subida."""
        self.upload_result.config(state=tk.NORMAL)
        self.upload_result.delete(1.0, tk.END)
        
        if status_code == 200 and result.get('success'):
            self.upload_result.insert(tk.END, "[OK] Archivo subido y firmado exitosamente!\n\n")
            self.upload_result.insert(tk.END, f"Archivo: {result['filename']}\n")
            self.upload_result.insert(tk.END, f"Tamaño: {result['size']} bytes\n")
            self.upload_result.insert(tk.END, f"Firma guardada en: {result['signature_path']}\n")
            self.upload_result.insert(tk.END, f"Hash SHA256: {result['signature']['hash']}\n")
            self.upload_result.insert(tk.END, f"Algoritmo: {result['signature']['algorithm']}\n")
            self.upload_result.insert(tk.END, f"Timestamp: {result['signature']['timestamp']}\n")
            
            # Limpiar campo de archivo
            self.file_path_var.set("")
            
            # Actualizar lista de archivos
            self.load_files_list()
        else:
            self.upload_result.insert(tk.END, f"[ERROR] {result.get('error', 'Error desconocido')}\n")
        
        self.upload_result.config(state=tk.DISABLED)
    
    def load_files_list(self):
        """Carga la lista de archivos subidos."""
        def load_thread():
            try:
                response = requests.get(f"{self.base_url}/files", timeout=5)
                
                if response.status_code == 200:
                    result = response.json()
                    files = result.get('files', [])
                    
                    # Actualizar listbox en pestaña de verificar
                    self.root.after(0, lambda: self.update_files_listbox(files))
                    
                    # Actualizar display en pestaña de listar
                    self.root.after(0, lambda: self.update_files_display(files))
                else:
                    self.root.after(0, lambda: self.show_error("Error al cargar archivos"))
                    
            except requests.exceptions.ConnectionError:
                self.root.after(0, lambda: self.show_error("No se pudo conectar al servidor"))
            except Exception as e:
                self.root.after(0, lambda: self.show_error(f"Error: {str(e)}"))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def update_files_listbox(self, files):
        """Actualiza el listbox de archivos."""
        self.files_listbox.delete(0, tk.END)
        for file_info in files:
            self.files_listbox.insert(tk.END, file_info['filename'])
    
    def update_files_display(self, files):
        """Actualiza el display de archivos."""
        if not hasattr(self, 'files_display'):
            return
        self.files_display.config(state=tk.NORMAL)
        self.files_display.delete(1.0, tk.END)
        
        if not files:
            self.files_display.insert(tk.END, "No hay archivos subidos.\n")
        else:
            self.files_display.insert(tk.END, f"Total de archivos: {len(files)}\n\n")
            self.files_display.insert(tk.END, f"{'Archivo':<40} {'Tamaño':<15} {'Fecha':<25}\n")
            self.files_display.insert(tk.END, "-" * 80 + "\n")
            
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
                
                self.files_display.insert(tk.END, f"{filename:<40} {size_str:<15} {uploaded_at:<25}\n")
        
        self.files_display.config(state=tk.DISABLED)
    
    def verify_file(self):
        """Verifica la firma de un archivo seleccionado."""
        selection = self.files_listbox.curselection()
        
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona un archivo de la lista.")
            return
        
        filename = self.files_listbox.get(selection[0])
        
        self.verify_result.config(state=tk.NORMAL)
        self.verify_result.delete(1.0, tk.END)
        self.verify_result.insert(tk.END, f"Verificando firma de: {filename}...\n")
        self.verify_result.config(state=tk.DISABLED)
        
        def verify_thread():
            try:
                data = {'filename': filename}
                response = requests.post(
                    f"{self.base_url}/verify",
                    json=data,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                result = response.json()
                self.root.after(0, lambda: self.show_verify_result(result, filename))
                
            except requests.exceptions.ConnectionError:
                self.root.after(0, lambda: self.show_error("No se pudo conectar al servidor"))
            except Exception as e:
                self.root.after(0, lambda: self.show_error(f"Error: {str(e)}"))
        
        threading.Thread(target=verify_thread, daemon=True).start()
    
    def show_verify_result(self, result, filename):
        """Muestra el resultado de la verificación."""
        self.verify_result.config(state=tk.NORMAL)
        self.verify_result.delete(1.0, tk.END)
        
        if result.get('signature_valid'):
            self.verify_result.insert(tk.END, f"[OK] Firma VALIDA\n\n")
            self.verify_result.insert(tk.END, f"Archivo: {filename}\n")
            self.verify_result.insert(tk.END, f"Estado: El archivo NO ha sido modificado\n")
            self.verify_result.insert(tk.END, f"Verificado en: {result['verified_at']}\n")
            messagebox.showinfo("Verificación Exitosa", "La firma es válida. El archivo no ha sido modificado.")
        else:
            self.verify_result.insert(tk.END, f"[ERROR] Firma INVALIDA\n\n")
            self.verify_result.insert(tk.END, f"Archivo: {filename}\n")
            self.verify_result.insert(tk.END, f"Estado: El archivo FUE MODIFICADO\n")
            self.verify_result.insert(tk.END, f"Verificado en: {result['verified_at']}\n")
            messagebox.showerror("Verificación Fallida", "La firma es inválida. El archivo fue modificado después de firmarse.")
        
        self.verify_result.config(state=tk.DISABLED)
    
    def check_server_status(self):
        """Verifica el estado del servidor."""
        def check_thread():
            try:
                response = requests.get(f"{self.base_url}/health", timeout=3)
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get('status', 'unknown')
                    signer_available = result.get('signer_available', False)
                    
                    self.root.after(0, lambda: self.update_status(True, status, signer_available))
                else:
                    self.root.after(0, lambda: self.update_status(False, "Error", False))
                    
            except requests.exceptions.ConnectionError:
                self.root.after(0, lambda: self.update_status(False, "Desconectado", False))
            except Exception as e:
                self.root.after(0, lambda: self.update_status(False, f"Error: {str(e)}", False))
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    def update_status(self, connected, status, signer_available):
        """Actualiza el estado del servidor."""
        if connected:
            color = "#27ae60" if signer_available else "#f39c12"
            text = f"Servidor: {status.upper()} | Firmador: {'ACTIVO' if signer_available else 'INACTIVO'}"
        else:
            color = "#e74c3c"
            text = f"Servidor: {status}"
        
        self.status_label.config(text=text, fg=color)
        self.server_running = connected
    
    def show_error(self, message):
        """Muestra un error."""
        messagebox.showerror("Error", message)
    
    def go_back(self):
        """Vuelve al menú principal."""
        self.root.destroy()
        self.main_app.show_main()
    
    def on_closing(self):
        """Maneja el cierre de la ventana."""
        self.go_back()

