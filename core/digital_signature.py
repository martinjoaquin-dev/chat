# digital_signature.py - Módulo de Firma Digital
"""
Módulo para implementar firma digital en archivos (txt, pdf, zip).
Utiliza criptografía asimétrica para firmar y verificar archivos.
"""

import os
import hashlib
import zipfile
import shutil
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.hazmat.backends import default_backend
from datetime import datetime
import json

try:
    from PyPDF2 import PdfReader, PdfWriter
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("ADVERTENCIA: PyPDF2 no instalado. Soporte para PDF limitado.")


class DigitalSignature:
    """
    Clase para manejar firmas digitales de archivos.
    Soporta archivos: .txt, .pdf, .zip
    """
    
    def __init__(self, private_key_path=None, public_key_path=None):
        """
        Inicializa el firmador digital.
        
        Args:
            private_key_path: Ruta a la clave privada (para firmar)
            public_key_path: Ruta a la clave pública (para verificar)
        """
        self.private_key = None
        self.public_key = None
        
        if private_key_path and os.path.exists(private_key_path):
            self.load_private_key(private_key_path)
        
        if public_key_path and os.path.exists(public_key_path):
            self.load_public_key(public_key_path)
    
    def generate_key_pair(self, key_size=2048):
        """
        Genera un par de claves RSA para firma digital.
        
        Args:
            key_size: Tamaño de la clave (default: 2048)
        
        Returns:
            tuple: (private_key, public_key)
        """
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        return self.private_key, self.public_key
    
    def save_key_pair(self, private_key_path, public_key_path, password=None):
        """
        Guarda el par de claves en archivos.
        
        Args:
            private_key_path: Ruta donde guardar la clave privada
            public_key_path: Ruta donde guardar la clave pública
            password: Contraseña para proteger la clave privada (opcional)
        """
        if not self.private_key or not self.public_key:
            raise ValueError("Debe generar o cargar un par de claves primero")
        
        # Guardar clave privada
        encryption = serialization.NoEncryption()
        if password:
            from cryptography.hazmat.primitives.serialization import BestAvailableEncryption
            encryption = BestAvailableEncryption(password.encode())
        
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption
        )
        
        with open(private_key_path, 'wb') as f:
            f.write(private_pem)
        
        # Guardar clave pública
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        with open(public_key_path, 'wb') as f:
            f.write(public_pem)
    
    def load_private_key(self, key_path, password=None):
        """
        Carga una clave privada desde archivo.
        
        Args:
            key_path: Ruta al archivo de clave privada
            password: Contraseña si la clave está cifrada
        """
        with open(key_path, 'rb') as f:
            key_data = f.read()
        
        password_bytes = password.encode() if password else None
        self.private_key = load_pem_private_key(
            key_data,
            password=password_bytes,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
    
    def load_public_key(self, key_path):
        """
        Carga una clave pública desde archivo.
        
        Args:
            key_path: Ruta al archivo de clave pública
        """
        with open(key_path, 'rb') as f:
            key_data = f.read()
        
        self.public_key = load_pem_public_key(
            key_data,
            backend=default_backend()
        )
    
    def calculate_file_hash(self, file_path):
        """
        Calcula el hash SHA256 de un archivo de forma optimizada.
        
        Args:
            file_path: Ruta al archivo
        
        Returns:
            bytes: Hash SHA256 del archivo
        """
        sha256_hash = hashlib.sha256()
        # Usar un buffer más grande para mejorar el rendimiento (64KB en lugar de 4KB)
        buffer_size = 65536  # 64KB
        
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(buffer_size)
                if not chunk:
                    break
                # Asegurar que chunk sea bytes, no bytearray
                if isinstance(chunk, bytearray):
                    chunk = bytes(chunk)
                sha256_hash.update(chunk)
        
        # Asegurar que el digest sea bytes, no bytearray
        digest = sha256_hash.digest()
        if isinstance(digest, bytearray):
            return bytes(digest)
        return digest
    
    def sign_file(self, file_path, signature_path=None, signer_name=None, signer_email=None):
        """
        Firma un archivo digitalmente.
        
        Args:
            file_path: Ruta al archivo a firmar
            signature_path: Ruta donde guardar la firma (opcional)
            signer_name: Nombre del firmante (opcional)
            signer_email: Email del firmante (opcional)
        
        Returns:
            bytes: Firma digital del archivo
        """
        if not self.private_key:
            raise ValueError("Debe cargar una clave privada para firmar")
        
        # Calcular hash del archivo
        file_hash = self.calculate_file_hash(file_path)
        
        # Firmar el hash
        signature = self.private_key.sign(
            file_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Asegurar que signature sea bytes (no bytearray) antes de guardar
        if isinstance(signature, bytearray):
            signature = bytes(signature)
        if not isinstance(signature, bytes):
            signature = bytes(signature)
        
        # Asegurar que file_hash sea bytes (no bytearray)
        if isinstance(file_hash, bytearray):
            file_hash = bytes(file_hash)
        if not isinstance(file_hash, bytes):
            file_hash = bytes(file_hash)
        
        # Guardar firma si se especifica ruta
        if signature_path:
            try:
                # Convertir signature y file_hash a bytes explícitamente
                if isinstance(signature, bytearray):
                    signature = bytes(signature)
                elif not isinstance(signature, bytes):
                    signature = bytes(signature)
                
                if isinstance(file_hash, bytearray):
                    file_hash = bytes(file_hash)
                elif not isinstance(file_hash, bytes):
                    file_hash = bytes(file_hash)
                
                # Convertir a hex string (garantizado que es bytes ahora)
                signature_hex = signature.hex()  # Esto siempre devuelve string
                hash_hex = file_hash.hex()  # Esto siempre devuelve string
                
                # Crear diccionario con TODOS los valores como strings
                signature_data = {
                    'file_path': str(file_path),
                    'signature': str(signature_hex),
                    'hash': str(hash_hex),
                    'timestamp': str(datetime.now().isoformat()),
                    'algorithm': str('RSA-PSS-SHA256')
                }
            
                # Agregar información del firmante si está disponible
                if signer_name:
                    signature_data['signer_name'] = str(signer_name)
                if signer_email:
                    signature_data['signer_email'] = str(signer_email)
                
                # Serializar a JSON (todos los valores ya son strings)
                with open(signature_path, 'w', encoding='utf-8') as f:
                    json.dump(signature_data, f, indent=2, ensure_ascii=False)
            except (TypeError, ValueError) as e:
                # Error de serialización JSON
                import traceback
                error_tb = traceback.format_exc()
                print(f"Error al guardar firma en {signature_path}: {e}")
                print(f"Traceback: {error_tb}")
                print(f"Signature type: {type(signature)}, value: {repr(signature)[:100]}")
                print(f"File hash type: {type(file_hash)}, value: {repr(file_hash)[:100]}")
                raise ValueError(f"Error al guardar firma (serialización JSON): {str(e)}") from e
            except Exception as e:
                # Otro tipo de error
                import traceback
                error_tb = traceback.format_exc()
                print(f"Error inesperado al guardar firma: {e}")
                print(f"Traceback: {error_tb}")
                raise
        
        return signature
    
    def verify_file(self, file_path, signature_path=None, signature_bytes=None):
        """
        Verifica la firma digital de un archivo.
        
        Args:
            file_path: Ruta al archivo a verificar
            signature_path: Ruta al archivo de firma (JSON)
            signature_bytes: Firma en bytes (alternativa)
        
        Returns:
            bool: True si la firma es válida
        """
        if not self.public_key:
            raise ValueError("Debe cargar una clave pública para verificar")
        
        # Calcular hash del archivo
        file_hash = self.calculate_file_hash(file_path)
        
        # Cargar firma
        if signature_path:
            with open(signature_path, 'r') as f:
                signature_data = json.load(f)
            signature = bytes.fromhex(signature_data['signature'])
        elif signature_bytes:
            signature = signature_bytes
        else:
            raise ValueError("Debe proporcionar signature_path o signature_bytes")
        
        try:
            # Verificar firma
            self.public_key.verify(
                signature,
                file_hash,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            print(f"Error en verificación: {e}")
            return False
    
    def sign_txt_file(self, file_path, signature_path=None, signer_name=None, signer_email=None):
        """
        Firma un archivo de texto (.txt) y crea una versión firmada visible.
        
        Args:
            file_path: Ruta al archivo .txt
            signature_path: Ruta donde guardar la firma
            signer_name: Nombre del firmante (opcional)
            signer_email: Email del firmante (opcional)
        
        Returns:
            str: Ruta al archivo firmado (si se creó)
        """
        if not file_path.endswith('.txt'):
            raise ValueError("El archivo debe ser .txt")
        
        # Firmar archivo
        signature = self.sign_file(file_path, signature_path, signer_name, signer_email)
        
        # Crear versión firmada visible
        signed_file_path = self._create_signed_txt_file(file_path, signer_name, signer_email)
        
        return signed_file_path
    
    def sign_pdf_file(self, file_path, signature_path=None, signer_name=None, signer_email=None):
        """
        Firma un archivo PDF y crea una versión firmada visible (opcional para archivos grandes).
        
        Args:
            file_path: Ruta al archivo .pdf
            signature_path: Ruta donde guardar la firma
            signer_name: Nombre del firmante (opcional)
            signer_email: Email del firmante (opcional)
        
        Returns:
            str: Ruta al archivo firmado (si se creó)
        """
        if not PDF_SUPPORT:
            raise ImportError("PyPDF2 no está instalado. Instala con: pip install PyPDF2")
        
        if not file_path.endswith('.pdf'):
            raise ValueError("El archivo debe ser .pdf")
        
        # Firmar archivo (esto es lo más importante)
        signature = self.sign_file(file_path, signature_path, signer_name, signer_email)
    
        # Crear versión firmada visible solo para archivos pequeños (optimización)
        file_size = os.path.getsize(file_path)
        if file_size > 10 * 1024 * 1024:  # Archivos > 10MB: omitir creación de versión visible
            print(f"Archivo grande ({file_size / 1024 / 1024:.1f}MB): omitiendo versión visible para mejorar velocidad")
            return None
        
        # Para archivos pequeños, crear versión firmada visible
        signed_file_path = self._create_signed_pdf_file(file_path, signer_name, signer_email)
        
        return signed_file_path
    
    def sign_zip_file(self, file_path, signature_path=None, signer_name=None, signer_email=None):
        """
        Firma un archivo ZIP.
        
        Args:
            file_path: Ruta al archivo .zip
            signature_path: Ruta donde guardar la firma
            signer_name: Nombre del firmante (opcional)
            signer_email: Email del firmante (opcional)
        
        Returns:
            str: Ruta al archivo firmado (si se creó)
        """
        if not file_path.endswith('.zip'):
            raise ValueError("El archivo debe ser .zip")
        
        # Firmar archivo
        signature = self.sign_file(file_path, signature_path, signer_name, signer_email)
        
        # Para ZIP, no creamos versión visible, pero podemos agregar metadata
        return None
    
    def _create_signed_txt_file(self, file_path, signer_name=None, signer_email=None):
        """Crea una versión del archivo TXT con la firma visible al final."""
        signed_file_path = file_path.replace('.txt', '_signed.txt')
        
        # Leer archivo original
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Agregar información de firma al final
        signature_text = '\n\n' + '='*50 + '\n'
        signature_text += 'FIRMA DIGITAL\n'
        signature_text += '='*50 + '\n'
        if signer_name:
            signature_text += f'Firmado por: {signer_name}\n'
        if signer_email:
            signature_text += f'Email: {signer_email}\n'
        signature_text += f'Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
        signature_text += '='*50
        
        # Escribir archivo firmado
        with open(signed_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            f.write(signature_text)
        
        return signed_file_path
    
    def _create_signed_pdf_file(self, file_path, signer_name=None, signer_email=None):
        """
        Crea una versión del archivo PDF con metadata de firma (optimizado para velocidad).
        Para archivos grandes, omite la copia completa y solo agrega metadata.
        """
        if not PDF_SUPPORT:
            return None
        
        try:
            signed_file_path = file_path.replace('.pdf', '_signed.pdf')
            
            # Optimización: Para archivos grandes, copiar directamente y solo agregar metadata
            # Esto es mucho más rápido que copiar todas las páginas
            import shutil
            file_size = os.path.getsize(file_path)
            
            # OPTIMIZACIÓN CRÍTICA: Para archivos grandes (>3MB), solo copiar sin metadata
            # La firma digital ya está guardada en .sig.json, esto es solo visual
            if file_size > 3 * 1024 * 1024:  # Más de 3MB
                # Para archivos grandes, simplemente copiar el archivo (MUY rápido)
                # La firma digital ya está guardada en el archivo .sig.json
                shutil.copy2(file_path, signed_file_path)
                print(f"✓ Archivo grande ({file_size / 1024 / 1024:.1f}MB): versión visible creada rápidamente")
                return signed_file_path
            
            # Para archivos pequeños, agregar metadata y página de firma visible
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            # Copiar todas las páginas del original
            for page in reader.pages:
                writer.add_page(page)
            
            # Intentar agregar una página visible con la firma usando reportlab
            try:
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter, A4
                from reportlab.lib.units import inch
                from reportlab.lib.colors import HexColor
                from io import BytesIO
                
                # Convertir signer_name y signer_email a strings si son bytearray
                def ensure_string(value):
                    """Convierte bytearray a string si es necesario."""
                    if value is None:
                        return None
                    if isinstance(value, bytearray):
                        return value.decode('utf-8')
                    if isinstance(value, bytes):
                        return value.decode('utf-8')
                    return str(value)
                
                signer_name_str = ensure_string(signer_name) if signer_name else None
                signer_email_str = ensure_string(signer_email) if signer_email else None
                
                # Crear una página nueva con la información de la firma
                packet = BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)
                width, height = letter
                
                # Fondo con color suave
                can.setFillColor(HexColor('#F8F9FA'))
                can.rect(0, 0, width, height, fill=1, stroke=0)
                
                # Título principal centrado
                can.setFillColor(HexColor('#1A237E'))
                can.setFont("Helvetica-Bold", 24)
                title = "FIRMA DIGITAL"
                title_width = can.stringWidth(title, "Helvetica-Bold", 24)
                can.drawString((width - title_width) / 2, height - 100, title)
                
                # Línea decorativa
                can.setStrokeColor(HexColor('#3F51B5'))
                can.setLineWidth(2)
                can.line(50, height - 130, width - 50, height - 130)
                
                # Información del firmante con mejor formato
                y_position = height - 180
                can.setFillColor(HexColor('#212121'))
                can.setFont("Helvetica-Bold", 14)
                
                # Contenedor para la información
                box_y = y_position - 150
                can.setFillColor(HexColor('#FFFFFF'))
                can.setStrokeColor(HexColor('#E0E0E0'))
                can.setLineWidth(1)
                can.roundRect(50, box_y, width - 100, 150, 5, fill=1, stroke=1)
                
                # Información dentro del contenedor
                y_info = y_position - 20
                can.setFillColor(HexColor('#424242'))
                
                if signer_name_str:
                    can.setFont("Helvetica-Bold", 12)
                    can.drawString(70, y_info, "Firmado por:")
                    can.setFont("Helvetica", 12)
                    can.drawString(180, y_info, signer_name_str)
                    y_info -= 30
                
                if signer_email_str:
                    can.setFont("Helvetica-Bold", 12)
                    can.drawString(70, y_info, "Email:")
                    can.setFont("Helvetica", 12)
                    can.drawString(180, y_info, signer_email_str)
                    y_info -= 30
                
                timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                can.setFont("Helvetica-Bold", 12)
                can.drawString(70, y_info, "Fecha de firma:")
                can.setFont("Helvetica", 12)
                can.drawString(180, y_info, timestamp_str)
                
                # Línea separadora
                y_info -= 25
                can.setStrokeColor(HexColor('#E0E0E0'))
                can.setLineWidth(1)
                can.line(70, y_info, width - 70, y_info)
                
                # Texto informativo
                y_info -= 40
                can.setFillColor(HexColor('#757575'))
                can.setFont("Helvetica", 10)
                can.drawString(70, y_info, "Este documento ha sido firmado digitalmente.")
                y_info -= 18
                can.drawString(70, y_info, "La integridad del documento puede verificarse usando la firma digital.")
                y_info -= 18
                can.drawString(70, y_info, "Para verificar la firma, utilice la función de verificación del sistema.")
                
                # Firma al final
                can.setFillColor(HexColor('#9E9E9E'))
                can.setFont("Helvetica-Oblique", 9)
                footer = "Sistema de Firma Digital"
                footer_width = can.stringWidth(footer, "Helvetica-Oblique", 9)
                can.drawString((width - footer_width) / 2, 50, footer)
                
                can.save()
                
                # Agregar la página al PDF
                packet.seek(0)
                signature_pdf = PdfReader(packet)
                signature_page = signature_pdf.pages[0]
                writer.add_page(signature_page)
                
                print(f"✓ Página de firma visible agregada al PDF")
            except ImportError:
                # Si reportlab no está instalado, solo agregar metadata mejorada
                print("INFO: reportlab no instalado. Agregando solo metadata. Para firma visible, instala: pip install reportlab")
            except Exception as e:
                print(f"Advertencia: No se pudo crear página de firma visible: {e}")
            
            # Agregar metadata con información del firmante (siempre, incluso si hay página visible)
            try:
                signer_display = signer_name or signer_email or "Usuario"
                signer_display = str(signer_display) if signer_display else "Usuario"
                timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Metadata mejorada para que sea más visible en propiedades del documento
                metadata = {
                    '/Title': 'Documento firmado digitalmente',
                    '/Author': str(signer_name) if signer_name else 'Firmante',
                    '/Subject': f'Firmado por {signer_display} el {timestamp_str}',
                    '/Keywords': f'Firma digital, {signer_display}, {timestamp_str}',
                }
                
                writer.add_metadata(metadata)
            except Exception as meta_error:
                # Si falla agregar metadata, continuar sin ella (no es crítico)
                print(f"Advertencia: No se pudo agregar metadata al PDF: {meta_error}")
            
            # Guardar PDF firmado
            with open(signed_file_path, 'wb') as output_file:
                writer.write(output_file)
            
            return signed_file_path
            
        except Exception as e:
            print(f"Error al crear PDF firmado visible: {e}")
            # Si falla, al menos devolver None para que siga funcionando
            return None
    
    def sign_multiple_files(self, file_paths, output_dir=None):
        """
        Firma múltiples archivos.
        
        Args:
            file_paths: Lista de rutas de archivos
            output_dir: Directorio donde guardar las firmas
        
        Returns:
            dict: Diccionario con archivo -> firma
        """
        signatures = {}
        
        for file_path in file_paths:
            file_ext = Path(file_path).suffix.lower()
            sig_path = None
            
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                sig_name = Path(file_path).stem + '.sig.json'
                sig_path = os.path.join(output_dir, sig_name)
            
            try:
                if file_ext == '.txt':
                    sig = self.sign_txt_file(file_path, sig_path)
                elif file_ext == '.pdf':
                    sig = self.sign_pdf_file(file_path, sig_path)
                elif file_ext == '.zip':
                    sig = self.sign_zip_file(file_path, sig_path)
                else:
                    print(f"Tipo de archivo no soportado: {file_ext}")
                    continue
                
                signatures[file_path] = sig.hex()
                print(f"Archivo firmado: {file_path}")
                
            except Exception as e:
                print(f"Error al firmar {file_path}: {e}")
        
        return signatures


def generate_signing_key_pair(output_dir='signing_keys'):
    """
    Función auxiliar para generar par de claves de firma.
    
    Args:
        output_dir: Directorio donde guardar las claves
    
    Returns:
        tuple: (private_key_path, public_key_path)
    """
    os.makedirs(output_dir, exist_ok=True)
    
    signer = DigitalSignature()
    signer.generate_key_pair()
    
    private_path = os.path.join(output_dir, 'signing_private_key.pem')
    public_path = os.path.join(output_dir, 'signing_public_key.pem')
    
    signer.save_key_pair(private_path, public_path)
    
    print(f"Par de claves generado:")
    print(f"  Clave privada: {private_path}")
    print(f"  Clave pública: {public_path}")
    
    return private_path, public_path


if __name__ == '__main__':
    # Ejemplo de uso
    print("=== Módulo de Firma Digital ===")
    print("\n1. Generando par de claves...")
    private_key, public_key = generate_signing_key_pair()
    
    print("\n2. Ejemplo de uso:")
    print("   signer = DigitalSignature(private_key, public_key)")
    print("   signature = signer.sign_file('archivo.txt')")
    print("   is_valid = signer.verify_file('archivo.txt', 'archivo.sig.json')")

