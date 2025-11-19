# digital_signature.py - Módulo de Firma Digital
"""
Módulo para implementar firma digital en archivos (txt, pdf, zip).
Utiliza criptografía asimétrica para firmar y verificar archivos.
"""

import os
import hashlib
import zipfile
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
        Calcula el hash SHA256 de un archivo.
        
        Args:
            file_path: Ruta al archivo
        
        Returns:
            bytes: Hash SHA256 del archivo
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256_hash.update(chunk)
        return sha256_hash.digest()
    
    def sign_file(self, file_path, signature_path=None):
        """
        Firma un archivo digitalmente.
        
        Args:
            file_path: Ruta al archivo a firmar
            signature_path: Ruta donde guardar la firma (opcional)
        
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
        
        # Guardar firma si se especifica ruta
        if signature_path:
            signature_data = {
                'file_path': file_path,
                'signature': signature.hex(),
                'hash': file_hash.hex(),
                'timestamp': datetime.now().isoformat(),
                'algorithm': 'RSA-PSS-SHA256'
            }
            
            with open(signature_path, 'w') as f:
                json.dump(signature_data, f, indent=2)
        
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
    
    def sign_txt_file(self, file_path, signature_path=None):
        """
        Firma un archivo de texto (.txt).
        
        Args:
            file_path: Ruta al archivo .txt
            signature_path: Ruta donde guardar la firma
        
        Returns:
            bytes: Firma digital
        """
        if not file_path.endswith('.txt'):
            raise ValueError("El archivo debe ser .txt")
        
        return self.sign_file(file_path, signature_path)
    
    def sign_pdf_file(self, file_path, signature_path=None):
        """
        Firma un archivo PDF.
        
        Args:
            file_path: Ruta al archivo .pdf
            signature_path: Ruta donde guardar la firma
        
        Returns:
            bytes: Firma digital
        """
        if not PDF_SUPPORT:
            raise ImportError("PyPDF2 no está instalado. Instala con: pip install PyPDF2")
        
        if not file_path.endswith('.pdf'):
            raise ValueError("El archivo debe ser .pdf")
        
        return self.sign_file(file_path, signature_path)
    
    def sign_zip_file(self, file_path, signature_path=None):
        """
        Firma un archivo ZIP.
        
        Args:
            file_path: Ruta al archivo .zip
            signature_path: Ruta donde guardar la firma
        
        Returns:
            bytes: Firma digital
        """
        if not file_path.endswith('.zip'):
            raise ValueError("El archivo debe ser .zip")
        
        return self.sign_file(file_path, signature_path)
    
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

