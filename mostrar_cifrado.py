"""
Script para mostrar la estructura completa del cifrado.
"""

from crypto_utils import SymmetricCrypto
import binascii

def mostrar_estructura_completa():
    print("=== ESTRUCTURA COMPLETA DEL CIFRADO ===\n")
    
    crypto = SymmetricCrypto("mi_clave_secreta")
    
    mensaje = "Hola mundo!"
    print(f"📝 Mensaje original: '{mensaje}'")
    print(f"📏 Longitud: {len(mensaje)} caracteres")
    print()
    
    payload_cifrado = crypto.encrypt_message_payload(mensaje)
    
    print("🔐 ESTRUCTURA DEL PAYLOAD CIFRADO:")
    print(f"   Total: {len(payload_cifrado)} bytes")
    print()
    
    iv = payload_cifrado[0:12]
    tag = payload_cifrado[12:28]
    hmac_digest = payload_cifrado[28:60]
    ciphertext = payload_cifrado[60:]
    
    print("📋 COMPONENTES:")
    print(f"   IV (12 bytes):     {binascii.hexlify(iv).decode()}")
    print(f"   Tag (16 bytes):    {binascii.hexlify(tag).decode()}")
    print(f"   HMAC (32 bytes):   {binascii.hexlify(hmac_digest).decode()}")
    print(f"   Ciphertext:        {binascii.hexlify(ciphertext[:20]).decode()}...")
    print()
    
    print("📡 DATOS COMPLETOS QUE VIAJAN POR LA RED:")
    print(f"   {binascii.hexlify(payload_cifrado).decode()}")
    print()
    
    mensaje_descifrado = crypto.decrypt_message(payload_cifrado)
    print(f"🔓 Mensaje descifrado: '{mensaje_descifrado}'")
    
    if mensaje == mensaje_descifrado:
        print("✅ Cifrado/descifrado exitoso!")
    else:
        print("❌ Error en el proceso")

def comparar_con_sin_cifrado():
    print("\n=== COMPARACIÓN: CON vs SIN CIFRADO ===\n")
    
    mensaje = "Información confidencial"
    
    print("❌ SIN CIFRADO:")
    datos_sin_cifrar = mensaje.encode('utf-8')
    print(f"   Mensaje: '{mensaje}'")
    print(f"   En la red: {datos_sin_cifrar}")
    print(f"   ¿Se puede leer? SÍ - '{datos_sin_cifrar.decode()}'")
    print()
    
    print("✅ CON CIFRADO:")
    crypto = SymmetricCrypto("clave_secreta")
    datos_cifrados = crypto.encrypt_message_payload(mensaje)
    print(f"   Mensaje: '{mensaje}'")
    print(f"   En la red: {binascii.hexlify(datos_cifrados[:30]).decode()}...")
    print("   ¿Se puede leer? NO - Son datos cifrados")
    print("   🔒 Necesita la clave para descifrar")

if __name__ == "__main__":
    mostrar_estructura_completa()
    comparar_con_sin_cifrado()
