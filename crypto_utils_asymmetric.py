# crypto_utils_asymmetric.py
"""
Módulo de utilidades criptográficas para el chat asimétrico.
Implementa RSA-4096 + ECDH P-384 + AES-256-GCM + HMAC para comunicación segura.
"""

import os
import struct
import hmac
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


class AsymmetricCrypto:
    """
    Clase para manejar cifrado asimétrico usando RSA-4096 + ECDH P-384 + AES-256-GCM.
    """
    
    def __init__(self, key_size: int = 4096):
        """
        Inicializa el cifrador asimétrico.
        
        Args:
            key_size: Tamaño de la clave RSA (default: 4096)
        """
        self.key_size = key_size
        self.rsa_private_key = None
        self.rsa_public_key = None
        self.ecdh_private_key = None
        self.ecdh_public_key = None
        self.shared_secret = None
        self.aes_key = None
        self.aesgcm = None
        
    def generate_rsa_keys(self):
        """Genera par de claves RSA."""
        self.rsa_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.key_size,
            backend=default_backend()
        )
        self.rsa_public_key = self.rsa_private_key.public_key()
        
    def generate_ecdh_keys(self):
        """Genera par de claves ECDH."""
        self.ecdh_private_key = ec.generate_private_key(
            curve=ec.SECP384R1(),
            backend=default_backend()
        )
        self.ecdh_public_key = self.ecdh_private_key.public_key()
        
    def get_rsa_public_key_pem(self) -> bytes:
        """Obtiene la clave pública RSA en formato PEM."""
        if not self.rsa_public_key:
            self.generate_rsa_keys()
        
        return self.rsa_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    def get_ecdh_public_key_bytes(self) -> bytes:
        """Obtiene la clave pública ECDH como bytes."""
        if not self.ecdh_public_key:
            self.generate_ecdh_keys()
        
        return self.ecdh_public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
    
    def load_peer_rsa_public_key(self, pem_data: bytes):
        """Carga la clave pública RSA del peer."""
        return serialization.load_pem_public_key(pem_data, backend=default_backend())
    
    def load_peer_ecdh_public_key(self, key_bytes: bytes):
        """Carga la clave pública ECDH del peer."""
        return ec.EllipticCurvePublicKey.from_encoded_point(
            curve=ec.SECP384R1(),
            data=key_bytes
        )
    
    def compute_shared_secret(self, peer_ecdh_public_key):
        """Calcula el secreto compartido usando ECDH."""
        self.shared_secret = self.ecdh_private_key.exchange(
            ec.ECDH(),
            peer_ecdh_public_key
        )
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'chat_aes_key',
            backend=default_backend()
        )
        self.aes_key = hkdf.derive(self.shared_secret)
        self.aesgcm = AESGCM(self.aes_key)
    
    def encrypt_message(self, plaintext: str) -> bytes:
        """
        Cifra un mensaje usando AES-256-GCM.
        
        Args:
            plaintext: Mensaje a cifrar
            
        Returns:
            bytes: Mensaje cifrado con estructura completa
        """
        if not self.aesgcm:
            raise ValueError("No hay clave AES disponible. Ejecuta intercambio de claves primero.")
        
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
        Cifra un mensaje (solo payload, sin longitud).
        
        Args:
            plaintext: Mensaje a cifrar
            
        Returns:
            bytes: Payload cifrado (sin longitud)
        """
        if not self.aesgcm:
            raise ValueError("No hay clave AES disponible. Ejecuta intercambio de claves primero.")
        
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
        if not self.aesgcm:
            raise ValueError("No hay clave AES disponible. Ejecuta intercambio de claves primero.")
        
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
    
    def sign_message(self, message: str) -> bytes:
        """
        Firma digitalmente un mensaje con RSA.
        
        Args:
            message: Mensaje a firmar
            
        Returns:
            bytes: Firma digital
        """
        if not self.rsa_private_key:
            raise ValueError("No hay clave privada RSA disponible")
        
        message_bytes = message.encode('utf-8')
        signature = self.rsa_private_key.sign(
            message_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature
    
    def verify_signature(self, message: str, signature: bytes, public_key) -> bool:
        """
        Verifica una firma digital.
        
        Args:
            message: Mensaje original
            signature: Firma digital
            public_key: Clave pública del firmante
            
        Returns:
            bool: True si la firma es válida
        """
        try:
            message_bytes = message.encode('utf-8')
            public_key.verify(
                signature,
                message_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    def _derive_hmac_key(self) -> bytes:
        """
        Deriva una clave separada para HMAC.
        
        Returns:
            bytes: Clave HMAC de 32 bytes
        """
        if not self.shared_secret:
            raise ValueError("No hay secreto compartido disponible")
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'chat_hmac_salt',
            info=b'chat_hmac_key',
            backend=default_backend()
        )
        return hkdf.derive(self.shared_secret)
    
    def get_public_key_hash(self) -> str:
        """
        Obtiene un hash de la clave pública RSA para identificación.
        
        Returns:
            str: Hash hexadecimal de la clave pública
        """
        if not self.rsa_public_key:
            self.generate_rsa_keys()
        
        public_key_bytes = self.rsa_public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return hashlib.sha256(public_key_bytes).hexdigest()[:16]


def test_asymmetric_crypto():
    """
    Función de prueba para verificar que el cifrado asimétrico funciona correctamente.
    """
    print("=== PROBANDO CIFRADO ASIMETRICO ===\n")
    
    crypto_client = AsymmetricCrypto()
    crypto_server = AsymmetricCrypto()
    
    print("🔑 Generando claves RSA y ECDH...")
    crypto_client.generate_rsa_keys()
    crypto_client.generate_ecdh_keys()
    crypto_server.generate_rsa_keys()
    crypto_server.generate_ecdh_keys()
    
    print("🔄 Intercambiando claves públicas...")
    client_rsa_pem = crypto_client.get_rsa_public_key_pem()
    client_ecdh_bytes = crypto_client.get_ecdh_public_key_bytes()
    server_rsa_pem = crypto_server.get_rsa_public_key_pem()
    server_ecdh_bytes = crypto_server.get_ecdh_public_key_bytes()
    
    client_peer_rsa = crypto_client.load_peer_rsa_public_key(server_rsa_pem)
    client_peer_ecdh = crypto_client.load_peer_ecdh_public_key(server_ecdh_bytes)
    server_peer_rsa = crypto_server.load_peer_rsa_public_key(client_rsa_pem)
    server_peer_ecdh = crypto_server.load_peer_ecdh_public_key(client_ecdh_bytes)
    
    print("🤝 Calculando secreto compartido ECDH...")
    crypto_client.compute_shared_secret(server_peer_ecdh)
    crypto_server.compute_shared_secret(client_peer_ecdh)
    
    test_message = "¡Hola! Este es un mensaje de prueba para el chat asimétrico."
    print(f"📝 Mensaje original: {test_message}")
    print()
    
    print("🔐 Cifrando mensaje...")
    encrypted_payload = crypto_client.encrypt_message_payload(test_message)
    print(f"📦 Payload cifrado: {len(encrypted_payload)} bytes")
    
    print("✍️ Firmando mensaje...")
    signature = crypto_client.sign_message(test_message)
    print(f"📝 Firma digital: {len(signature)} bytes")
    
    print("🔓 Descifrando mensaje...")
    decrypted_message = crypto_server.decrypt_message(encrypted_payload)
    print(f"📝 Mensaje descifrado: {decrypted_message}")
    
    print("✅ Verificando firma...")
    signature_valid = crypto_server.verify_signature(decrypted_message, signature, client_peer_rsa)
    print(f"🔍 Firma válida: {signature_valid}")
    
    if test_message == decrypted_message and signature_valid:
        print("\n✅ CIFRADO ASIMETRICO EXITOSO!")
        print("   - Intercambio de claves: ✅")
        print("   - Cifrado/descifrado: ✅")
        print("   - Firma digital: ✅")
        print("   - Verificación: ✅")
    else:
        print("\n❌ ERROR en cifrado asimétrico")
    
    print(f"\n🆔 ID Cliente: {crypto_client.get_public_key_hash()}")
    print(f"🆔 ID Servidor: {crypto_server.get_public_key_hash()}")


if __name__ == "__main__":
    test_asymmetric_crypto()
