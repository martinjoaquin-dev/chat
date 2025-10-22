"""
Script para mostrar la estructura completa del cifrado asimétrico.
"""

from crypto_utils_asymmetric import AsymmetricCrypto
import binascii

def mostrar_estructura_asimetrica():
    print("=== ESTRUCTURA COMPLETA DEL CIFRADO ASIMETRICO ===\n")
    
    crypto_client = AsymmetricCrypto()
    crypto_server = AsymmetricCrypto()
    
    print("🔑 Generando claves RSA-4096 y ECDH P-384...")
    crypto_client.generate_rsa_keys()
    crypto_client.generate_ecdh_keys()
    crypto_server.generate_rsa_keys()
    crypto_server.generate_ecdh_keys()
    
    print(f"🆔 ID Cliente: {crypto_client.get_public_key_hash()}")
    print(f"🆔 ID Servidor: {crypto_server.get_public_key_hash()}")
    print()
    
    print("🔄 Intercambiando claves públicas...")
    client_rsa_pem = crypto_client.get_rsa_public_key_pem()
    client_ecdh_bytes = crypto_client.get_ecdh_public_key_bytes()
    server_rsa_pem = crypto_server.get_rsa_public_key_pem()
    server_ecdh_bytes = crypto_server.get_ecdh_public_key_bytes()
    
    print(f"📤 Clave RSA Cliente: {len(client_rsa_pem)} bytes")
    print(f"📤 Clave ECDH Cliente: {len(client_ecdh_bytes)} bytes")
    print(f"📤 Clave RSA Servidor: {len(server_rsa_pem)} bytes")
    print(f"📤 Clave ECDH Servidor: {len(server_ecdh_bytes)} bytes")
    print()
    
    client_peer_rsa = crypto_client.load_peer_rsa_public_key(server_rsa_pem)
    client_peer_ecdh = crypto_client.load_peer_ecdh_public_key(server_ecdh_bytes)
    server_peer_rsa = crypto_server.load_peer_rsa_public_key(client_rsa_pem)
    server_peer_ecdh = crypto_server.load_peer_ecdh_public_key(client_ecdh_bytes)
    
    print("🤝 Calculando secreto compartido ECDH...")
    crypto_client.compute_shared_secret(server_peer_ecdh)
    crypto_server.compute_shared_secret(client_peer_ecdh)
    print("✅ Secreto compartido calculado")
    print()
    
    mensaje = "¡Hola! Este es un mensaje de prueba para el chat asimétrico."
    print(f"📝 Mensaje original: '{mensaje}'")
    print(f"📏 Longitud: {len(mensaje)} caracteres")
    print()
    
    print("🔐 CIFRANDO MENSAJE...")
    encrypted_payload = crypto_client.encrypt_message_payload(mensaje)
    print(f"📦 Payload cifrado: {len(encrypted_payload)} bytes")
    
    print("\n🏗️ ESTRUCTURA DEL MENSAJE CIFRADO:")
    iv = encrypted_payload[0:12]
    tag = encrypted_payload[12:28]
    hmac_digest = encrypted_payload[28:60]
    ciphertext = encrypted_payload[60:]
    
    print(f"   IV (12 bytes):     {binascii.hexlify(iv).decode()}")
    print(f"   Tag (16 bytes):    {binascii.hexlify(tag).decode()}")
    print(f"   HMAC (32 bytes):   {binascii.hexlify(hmac_digest).decode()}")
    print(f"   Ciphertext:        {binascii.hexlify(ciphertext[:20]).decode()}...")
    print()
    
    print("✍️ FIRMANDO MENSAJE...")
    signature = crypto_client.sign_message(mensaje)
    print(f"📝 Firma digital: {len(signature)} bytes")
    print(f"🔢 Firma (hex): {binascii.hexlify(signature[:30]).decode()}...")
    print()
    
    print("🔓 DESCIFRANDO MENSAJE...")
    decrypted_message = crypto_server.decrypt_message(encrypted_payload)
    print(f"📝 Mensaje descifrado: '{decrypted_message}'")
    print()
    
    print("✅ VERIFICANDO FIRMA DIGITAL...")
    signature_valid = crypto_server.verify_signature(decrypted_message, signature, client_peer_rsa)
    print(f"🔍 Firma válida: {signature_valid}")
    print()
    
    if mensaje == decrypted_message and signature_valid:
        print("✅ CIFRADO ASIMETRICO EXITOSO!")
        print("   - Intercambio de claves: ✅")
        print("   - Cifrado/descifrado: ✅")
        print("   - Firma digital: ✅")
        print("   - Verificación: ✅")
        print("   - No-repudio: ✅")
    else:
        print("❌ Error en cifrado asimétrico")
    print()

def comparar_simetrico_vs_asimetrico():
    print("=== COMPARACION: SIMETRICO vs ASIMETRICO ===\n")
    
    print("🔐 CIFRADO SIMETRICO:")
    print("   - Algoritmo: AES-256-GCM + HMAC-SHA256")
    print("   - Clave: Compartida predefinida")
    print("   - Ventajas: Rápido, simple")
    print("   - Desventajas: Distribución de claves, no-repudio")
    print()
    
    print("🔐 CIFRADO ASIMETRICO:")
    print("   - Algoritmo: RSA-4096 + ECDH P-384 + AES-256-GCM + HMAC-SHA256")
    print("   - Claves: Públicas/privadas, intercambio ECDH")
    print("   - Ventajas: No-repudio, distribución segura de claves")
    print("   - Desventajas: Más lento, más complejo")
    print()
    
    print("📊 COMPARACION DE RENDIMIENTO:")
    print("   - Simétrico: ~1ms por mensaje")
    print("   - Asimétrico: ~50ms por mensaje (intercambio de claves)")
    print("   - Asimétrico: ~5ms por mensaje (después del intercambio)")
    print()
    
    print("🎯 CASOS DE USO:")
    print("   - Simétrico: Chat grupal, comunicación interna")
    print("   - Asimétrico: Email seguro, transacciones, documentos legales")

def mostrar_protocolo_completo():
    print("=== PROTOCOLO COMPLETO ASIMETRICO ===\n")
    
    print("1️⃣ INTERCAMBIO DE CLAVES:")
    print("   Cliente → Servidor: Clave pública RSA + ECDH")
    print("   Servidor → Cliente: Clave pública RSA + ECDH")
    print("   Ambos calculan: Secreto compartido ECDH")
    print()
    
    print("2️⃣ CIFRADO DE MENSAJES:")
    print("   Cliente: Mensaje → AES-256-GCM → Payload cifrado")
    print("   Cliente: Mensaje → RSA-4096 → Firma digital")
    print("   Cliente: Envía payload + firma")
    print()
    
    print("3️⃣ DESCIFRADO Y VERIFICACION:")
    print("   Servidor: Recibe payload + firma")
    print("   Servidor: Payload → AES-256-GCM → Mensaje")
    print("   Servidor: Verifica firma RSA → Autenticidad")
    print("   Servidor: Log del mensaje con identidad verificada")
    print()
    
    print("🛡️ CARACTERISTICAS DE SEGURIDAD:")
    print("   - Confidencialidad: AES-256-GCM")
    print("   - Integridad: HMAC-SHA256")
    print("   - Autenticación: RSA-4096")
    print("   - No-repudio: Firma digital")
    print("   - Distribución de claves: ECDH P-384")

if __name__ == "__main__":
    mostrar_estructura_asimetrica()
    print("\n" + "="*60 + "\n")
    comparar_simetrico_vs_asimetrico()
    print("\n" + "="*60 + "\n")
    mostrar_protocolo_completo()
