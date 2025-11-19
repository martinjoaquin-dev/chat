# crypto_utils.py
"""
Módulo de utilidades criptográficas para el chat con cifrado híbrido.
Implementa cifrado híbrido: RSA para intercambio de claves + AES-256-GCM para mensajes.
"""

import os
import struct
import hmac
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class HybridCrypto:
    """
    Clase para manejar cifrado híbrido usando RSA + AES-256-GCM + HMAC-SHA256.
    - RSA: Para intercambio seguro de claves AES
    - AES-256-GCM: Para cifrado rápido de mensajes
    - HMAC-SHA256: Verificación de integridad del payload cifrado
    - SHA256: Verificación adicional de integridad del mensaje
    """
    
    def __init__(self):
        """
        Inicializa el cifrador híbrido generando un par de claves RSA.
        """
        # Generar par de claves RSA de 2048 bits
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        self.aes_key = None
        self.aesgcm = None
    
    def get_public_key_pem(self) -> bytes:
        """
        Obtiene la clave pública en formato PEM para intercambio.
        
        Returns:
            bytes: Clave pública en formato PEM
        """
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    def load_peer_public_key(self, public_key_pem: bytes):
        """
        Carga la clave pública del peer desde formato PEM.
        
        Args:
            public_key_pem: Clave pública en formato PEM
        """
        self.peer_public_key = serialization.load_pem_public_key(
            public_key_pem,
            backend=default_backend()
        )
    
    def generate_and_encrypt_aes_key(self) -> bytes:
        """
        Genera una clave AES aleatoria y la cifra con la clave pública del peer.
        
        Returns:
            bytes: Clave AES cifrada con RSA
        """
        if not hasattr(self, 'peer_public_key'):
            raise ValueError("Debe cargar la clave pública del peer primero")
        
        # Generar clave AES de 32 bytes (256 bits)
        self.aes_key = os.urandom(32)
        self.aesgcm = AESGCM(self.aes_key)
        
        # Cifrar la clave AES con RSA
        encrypted_key = self.peer_public_key.encrypt(
            self.aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return encrypted_key
    
    def decrypt_and_set_aes_key(self, encrypted_aes_key: bytes):
        """
        Descifra la clave AES recibida y la configura.
        
        Args:
            encrypted_aes_key: Clave AES cifrada con RSA
        """
        # Descifrar la clave AES con la clave privada RSA
        self.aes_key = self.private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        self.aesgcm = AESGCM(self.aes_key)
    
    def _derive_hmac_key(self) -> bytes:
        """
        Deriva una clave separada para HMAC desde la clave AES.
        Usa variable de entorno HMAC_SALT en lugar de valor hardcodeado.
        
        Returns:
            bytes: Clave HMAC de 32 bytes
        """
        # Obtener salt desde variable de entorno, con fallback seguro
        hmac_salt = os.getenv('HMAC_SALT', 'default_hmac_salt_change_in_production')
        if hmac_salt == 'default_hmac_salt_change_in_production':
            import warnings
            warnings.warn("HMAC_SALT no configurado en .env, usando valor por defecto. Configura en producción.", UserWarning)
        
        salt_bytes = hmac_salt.encode('utf-8')
        return hashlib.sha256(self.aes_key + salt_bytes).digest()
    
    def encrypt_message_payload(self, plaintext: str) -> bytes:
        """
        Cifra un mensaje de texto plano usando AES-256-GCM.
        
        Args:
            plaintext: Mensaje a cifrar
            
        Returns:
            bytes: Payload cifrado (sin longitud)
        """
        if self.aesgcm is None:
            raise ValueError("Debe establecer la clave AES primero")
        
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
        Descifra un mensaje cifrado usando AES-256-GCM.
        
        Args:
            encrypted_data: Payload cifrado (sin longitud)
            
        Returns:
            str: Mensaje descifrado
            
        Raises:
            ValueError: Si la verificación de integridad falla
        """
        if self.aesgcm is None:
            raise ValueError("Debe establecer la clave AES primero")
        
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
    
    def hash_message(self, message: str) -> str:
        """
        Calcula el hash SHA256 de un mensaje para verificación de integridad.
        
        Args:
            message: Mensaje de texto a hashear
            
        Returns:
            str: Hash SHA256 en formato hexadecimal
        """
        message_bytes = message.encode('utf-8')
        hash_obj = hashlib.sha256(message_bytes)
        return hash_obj.hexdigest()


# Mantener compatibilidad con código antiguo (deprecated)
class SymmetricCrypto:
    """
    Clase legacy para compatibilidad hacia atrás.
    DEPRECATED: Usar HybridCrypto en su lugar.
    """
    
    def __init__(self, password: str = "chat_secret_key_2024"):
        import warnings
        warnings.warn("SymmetricCrypto está deprecado. Usa HybridCrypto para mejor seguridad.", DeprecationWarning)
        
        self.password = password.encode('utf-8')
        self.key = self._derive_key()
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        self.aesgcm = AESGCM(self.key)
    
    def _derive_key(self) -> bytes:
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        salt = b'chat_salt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(self.password)
    
    def encrypt_message_payload(self, plaintext: str) -> bytes:
        iv = os.urandom(12)
        plaintext_bytes = plaintext.encode('utf-8')
        ciphertext = self.aesgcm.encrypt(iv, plaintext_bytes, None)
        ciphertext_only = ciphertext[:-16]
        tag = ciphertext[-16:]
        hmac_key = self._derive_hmac_key()
        hmac_digest = hmac.new(hmac_key, iv + ciphertext_only + tag, 'sha256').digest()
        return (iv + tag + hmac_digest + ciphertext_only)
    
    def decrypt_message(self, encrypted_data: bytes) -> str:
        if len(encrypted_data) < 60:
            raise ValueError("Datos cifrados demasiado cortos")
        iv = encrypted_data[0:12]
        tag = encrypted_data[12:28]
        hmac_digest = encrypted_data[28:60]
        ciphertext_only = encrypted_data[60:]
        hmac_key = self._derive_hmac_key()
        expected_hmac = hmac.new(hmac_key, iv + ciphertext_only + tag, 'sha256').digest()
        if not hmac.compare_digest(hmac_digest, expected_hmac):
            raise ValueError("Verificación HMAC falló")
        ciphertext = ciphertext_only + tag
        plaintext_bytes = self.aesgcm.decrypt(iv, ciphertext, None)
        return plaintext_bytes.decode('utf-8')
    
    def _derive_hmac_key(self) -> bytes:
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        salt = b'chat_hmac_salt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(self.password)
    
    def hash_message(self, message: str) -> str:
        message_bytes = message.encode('utf-8')
        hash_obj = hashlib.sha256(message_bytes)
        return hash_obj.hexdigest()


def test_crypto():
    """
    Función de prueba para verificar que el cifrado híbrido funciona correctamente.
    """
    print("Probando cifrado hibrido (RSA + AES)...")
    
    # Simular cliente y servidor
    cliente = HybridCrypto()
    servidor = HybridCrypto()
    
    # Intercambiar claves públicas
    cliente.load_peer_public_key(servidor.get_public_key_pem())
    servidor.load_peer_public_key(cliente.get_public_key_pem())
    
    # Cliente genera y cifra clave AES
    encrypted_aes_key = cliente.generate_and_encrypt_aes_key()
    servidor.decrypt_and_set_aes_key(encrypted_aes_key)
    
    # Ahora ambos tienen la misma clave AES
    # Cliente también necesita la clave (para este test, la copiamos)
    servidor_public_key_pem = servidor.get_public_key_pem()
    cliente2 = HybridCrypto()
    cliente2.load_peer_public_key(servidor_public_key_pem)
    encrypted_aes_key2 = cliente2.generate_and_encrypt_aes_key()
    servidor.decrypt_and_set_aes_key(encrypted_aes_key2)
    cliente2.decrypt_and_set_aes_key(encrypted_aes_key)
    
    test_message = "¡Hola! Este es un mensaje de prueba para el chat con cifrado hibrido."
    
    print(f"Mensaje original: {test_message}")
    
    # Cliente cifra mensaje
    encrypted = cliente2.encrypt_message_payload(test_message)
    print(f"Datos cifrados: {len(encrypted)} bytes")
    
    # Servidor descifra mensaje
    decrypted = servidor.decrypt_message(encrypted)
    print(f"Mensaje descifrado: {decrypted}")
    
    if test_message == decrypted:
        print("Cifrado/descifrado hibrido exitoso!")
    else:
        print("Error en cifrado/descifrado")
    
    # Verificar SHA256
    hash_cliente = cliente2.hash_message(test_message)
    hash_servidor = servidor.hash_message(decrypted)
    print(f"Hash SHA256 (cliente): {hash_cliente}")
    print(f"Hash SHA256 (servidor): {hash_servidor}")
    
    if hash_cliente == hash_servidor:
        print("Verificacion SHA256 exitosa!")


if __name__ == "__main__":
    test_crypto()
