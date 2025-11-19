#!/usr/bin/env python3
"""
Ventana del Chat Seguro con interfaz gráfica.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from core.client import main_client, create_ssl_context
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback si los imports fallan
    import importlib.util
    spec = importlib.util.spec_from_file_location("client", "core/client.py")
    client_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(client_module)
    main_client = client_module.main_client
    create_ssl_context = client_module.create_ssl_context

class ChatWindow:
    def __init__(self, root, main_app):
        self.root = root
        self.main_app = main_app
        self.root.title("Chat Seguro - Cliente")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.connected = False
        self.chat_loop = None
        self.chat_thread = None
        
        self.create_widgets()
        self.center_window()
        
        # Manejar cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
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
        # Frame superior - Conexión
        conn_frame = tk.Frame(self.root, bg="#34495e", padx=10, pady=10)
        conn_frame.pack(fill=tk.X)
        
        self.status_label = tk.Label(
            conn_frame,
            text="Desconectado",
            font=("Arial", 10, "bold"),
            bg="#34495e",
            fg="#e74c3c"
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.connect_btn = tk.Button(
            conn_frame,
            text="Conectar",
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            activebackground="#229954",
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=5,
            command=self.toggle_connection
        )
        self.connect_btn.pack(side=tk.RIGHT)
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#ecf0f1")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Área de mensajes
        messages_label = tk.Label(
            main_frame,
            text="Mensajes:",
            font=("Arial", 10, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        messages_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.messages_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="white",
            fg="#2c3e50",
            state=tk.DISABLED,
            height=20
        )
        self.messages_text.pack(fill=tk.BOTH, expand=True)
        
        # Frame inferior - Enviar mensaje
        send_frame = tk.Frame(main_frame, bg="#ecf0f1")
        send_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.message_entry = tk.Entry(
            send_frame,
            font=("Arial", 11),
            bg="white",
            fg="#2c3e50"
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", lambda e: self.send_message())
        
        self.send_btn = tk.Button(
            send_frame,
            text="Enviar",
            font=("Arial", 10, "bold"),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=5,
            command=self.send_message
        )
        self.send_btn.pack(side=tk.RIGHT)
        
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
    
    def add_message(self, message, sender="Sistema"):
        """Agrega un mensaje al área de texto."""
        self.messages_text.config(state=tk.NORMAL)
        
        if sender == "Sistema":
            self.messages_text.insert(tk.END, f"[{sender}] {message}\n", "system")
            self.messages_text.tag_config("system", foreground="#7f8c8d", font=("Arial", 9, "italic"))
        elif sender == "Tú":
            self.messages_text.insert(tk.END, f"[{sender}] {message}\n", "you")
            self.messages_text.tag_config("you", foreground="#3498db", font=("Arial", 10, "bold"))
        else:
            self.messages_text.insert(tk.END, f"[{sender}] {message}\n")
        
        self.messages_text.see(tk.END)
        self.messages_text.config(state=tk.DISABLED)
    
    def toggle_connection(self):
        """Conecta o desconecta del servidor."""
        if not self.connected:
            self.connect()
        else:
            self.disconnect()
    
    def connect(self):
        """Conecta al servidor."""
        self.add_message("Conectando al servidor...", "Sistema")
        self.status_label.config(text="Conectando...", fg="#f39c12")
        self.connect_btn.config(state=tk.DISABLED)
        
        # Conectar en un thread separado
        def connect_thread():
            try:
                import os
                from dotenv import load_dotenv
                load_dotenv()
                
                host = os.getenv('CLIENT_HOST', '127.0.0.1')
                port = int(os.getenv('CLIENT_PORT', '9000'))
                ssl_enabled = os.getenv('SSL_ENABLED', 'true').lower() == 'true'
                
                ssl_context = None
                if ssl_enabled:
                    ssl_context = create_ssl_context()
                
                # Ejecutar cliente asíncrono
                asyncio.run(main_client(host, port, ssl_context))
                
            except Exception as e:
                self.root.after(0, lambda: self.add_message(f"Error: {str(e)}", "Sistema"))
                self.root.after(0, lambda: self.status_label.config(text="Error", fg="#e74c3c"))
                self.root.after(0, lambda: self.connect_btn.config(state=tk.NORMAL, text="Conectar"))
        
        self.chat_thread = threading.Thread(target=connect_thread, daemon=True)
        self.chat_thread.start()
        
        # Simular conexión exitosa (en producción, esto vendría del cliente)
        self.root.after(1000, lambda: self.on_connected())
    
    def on_connected(self):
        """Callback cuando se conecta exitosamente."""
        self.connected = True
        self.status_label.config(text="Conectado", fg="#27ae60")
        self.connect_btn.config(text="Desconectar", state=tk.NORMAL)
        self.add_message("Conectado al servidor. Puedes enviar mensajes.", "Sistema")
    
    def disconnect(self):
        """Desconecta del servidor."""
        self.connected = False
        self.status_label.config(text="Desconectado", fg="#e74c3c")
        self.connect_btn.config(text="Conectar")
        self.add_message("Desconectado del servidor.", "Sistema")
    
    def send_message(self):
        """Envía un mensaje."""
        if not self.connected:
            messagebox.showwarning("No conectado", "Debes conectarte al servidor primero.")
            return
        
        message = self.message_entry.get().strip()
        if not message:
            return
        
        if message.lower() == 'quit':
            self.disconnect()
            return
        
        self.add_message(message, "Tú")
        self.message_entry.delete(0, tk.END)
        
        # Aquí se enviaría el mensaje al servidor
        # Por ahora solo lo mostramos localmente
    
    def go_back(self):
        """Vuelve al menú principal."""
        if self.connected:
            self.disconnect()
        self.root.destroy()
        self.main_app.show_main()
    
    def on_closing(self):
        """Maneja el cierre de la ventana."""
        if self.connected:
            self.disconnect()
        self.go_back()

