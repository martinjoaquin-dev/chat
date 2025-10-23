# crypto_utils.py
"""
Módulo de utilidades criptográficas para el chat simétrico.
Implementa cifrado AES-256-GCM con HMAC para autenticación adicional.
"""

import os
import struct
import hmac
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class SymmetricCrypto:
    """
    Clase para manejar cifrado simétrico usando AES-256-GCM + HMAC-SHA256.
    """
    
    def __init__(self, password: str = "chat_secret_key_2024"):
        """
        Inicializa el cifrador con una contraseña.
        
        Args:
            password: Contraseña para derivar la clave de cifrado
        """
        self.password = password.encode('utf-8')
        self.key = self._derive_key()
        self.aesgcm = AESGCM(self.key)
    
    def _derive_key(self) -> bytes:
        """
        Deriva una clave de 32 bytes usando PBKDF2.
        
        Returns:
            bytes: Clave derivada de 32 bytes
        """
        salt = b'chat_salt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(self.password)
    
    def encrypt_message(self, plaintext: str) -> bytes:
        """
        Cifra un mensaje de texto plano.
        
        Args:
            plaintext: Mensaje a cifrar
            
        Returns:
            bytes: Mensaje cifrado con estructura completa (incluye longitud)
        """
        iv = os.urandom(12)
        
        plaintext_bytes = plaintext.encode('utf-8')
        ciphertext = self.aesgcm.encrypt(iv, plaintext_bytes, None)
        
        ciphertext_only = ciphertext[:-16]
        tag = ciphertext[-16:]
        
        hmac_key = self._derive_hmac_key()
        hmac_digest = hmac.new(hmac_key, iv + ciphertext_only + tag, 'sha256').digest()
        
        total_length = 4 + 12 + 16 + 32 + len(ciphertext_only)
        
        return (struct.pack('!I', total_length) + 
                iv + 
                tag + 
                hmac_digest + 
                ciphertext_only)
    
    def encrypt_message_payload(self, plaintext: str) -> bytes:
        """
        Cifra un mensaje de texto plano (solo payload, sin longitud).
        
        Args:
            plaintext: Mensaje a cifrar
            
        Returns:
            bytes: Payload cifrado (sin longitud)
        """
        iv = os.urandom(12)
        
        plaintext_bytes = plaintext.encode('utf-8')
        ciphertext = self.aesgcm.encrypt(iv, plaintext_bytes, None)
        
        ciphertext_only = ciphertext[:-16]
        tag = ciphertext[-16:]
        
        hmac_key = self._derive_hmac_key()
        hmac_digest = hmac.new(hmac_key, iv + ciphertext_only + tag, 'sha256').digest()
        
        return (iv + 
                tag + 
                hmac_digest + 
                ciphertext_only)
    
    def decrypt_message(self, encrypted_data: bytes) -> str:
        """
        Descifra un mensaje cifrado (payload sin longitud).
        
        Args:
            encrypted_data: Payload cifrado (sin longitud)
            
        Returns:
            str: Mensaje descifrado
            
        Raises:
            ValueError: Si la verificación de integridad falla
        """
        if len(encrypted_data) < 60:
            raise ValueError("Datos cifrados demasiado cortos")
        
        iv = encrypted_data[0:12]
        tag = encrypted_data[12:28]
        hmac_digest = encrypted_data[28:60]
        ciphertext_only = encrypted_data[60:]
        
        hmac_key = self._derive_hmac_key()
        expected_hmac = hmac.new(hmac_key, iv + ciphertext_only + tag, 'sha256').digest()
        
        if not hmac.compare_digest(hmac_digest, expected_hmac):
            raise ValueError("Verificación HMAC falló - mensaje posiblemente alterado")
        
        ciphertext = ciphertext_only + tag
        plaintext_bytes = self.aesgcm.decrypt(iv, ciphertext, None)
        
        return plaintext_bytes.decode('utf-8')
    
    def _derive_hmac_key(self) -> bytes:
        """
        Deriva una clave separada para HMAC.
        
        Returns:
            bytes: Clave HMAC de 32 bytes
        """
        salt = b'chat_hmac_salt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(self.password)


def test_crypto():
    """
    Función de prueba para verificar que el cifrado funciona correctamente.
    """
    crypto = SymmetricCrypto()
    
    test_message = "¡Hola! Este es un mensaje de prueba para el chat cifrado."
    
    print("Probando cifrado simetrico...")
    print(f"Mensaje original: {test_message}")
    
    encrypted = crypto.encrypt_message(test_message)
    print(f"Datos cifrados: {len(encrypted)} bytes")
    
    decrypted = crypto.decrypt_message(encrypted)
    print(f"Mensaje descifrado: {decrypted}")
    
    if test_message == decrypted:
        print("Cifrado/descifrado exitoso!")
    else:
        print("Error en cifrado/descifrado")
    
    try:
        tampered_data = encrypted[:-10] + b'XXXXXXXXXX'
        crypto.decrypt_message(tampered_data)
        print("ERROR: Deberia haber fallado con datos alterados")
    except ValueError as e:
        print(f"Correcto: Detecto datos alterados - {e}")


if __name__ == "__main__":
    test_crypto()
