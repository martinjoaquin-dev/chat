"""
Script para generar certificados SSL/TLS autofirmados para desarrollo.
Para producción, usa certificados de una autoridad certificadora (CA) confiable.
"""

import os
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
import ipaddress

def generate_ssl_certificates():
    """Genera certificados SSL autofirmados para desarrollo."""
    
    # Crear directorio de certificados si no existe
    cert_dir = 'certificates'
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)
        print(f'Directorio {cert_dir} creado')
    
    # Generar clave privada
    print('Generando clave privada RSA...')
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Información del certificado
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Chat Application"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    
    # Crear certificado
    print('Generando certificado del servidor...')
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.DNSName("127.0.0.1"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Guardar certificado del servidor
    server_cert_path = os.path.join(cert_dir, 'server.crt')
    with open(server_cert_path, 'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    print(f'Certificado del servidor guardado en: {server_cert_path}')
    
    # Guardar clave privada del servidor
    server_key_path = os.path.join(cert_dir, 'server.key')
    with open(server_key_path, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    print(f'Clave privada del servidor guardada en: {server_key_path}')
    
    # Guardar certificado CA (mismo que el servidor para desarrollo)
    ca_cert_path = os.path.join(cert_dir, 'ca.crt')
    with open(ca_cert_path, 'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    print(f'Certificado CA guardado en: {ca_cert_path}')
    
    print('\n' + '='*60)
    print('Certificados SSL generados exitosamente!')
    print('='*60)
    print('\nADVERTENCIAS:')
    print('- Estos certificados son autofirmados y solo para desarrollo')
    print('- Para producción, usa certificados de una CA confiable')
    print('- Los navegadores mostrarán advertencias con estos certificados')
    print('\nPróximos pasos:')
    print('1. Configura SSL_ENABLED=true en tu archivo .env')
    print('2. Reinicia el servidor y cliente')
    print('3. Las conexiones ahora usarán SSL/TLS')

if __name__ == '__main__':
    try:
        generate_ssl_certificates()
    except Exception as e:
        print(f'Error al generar certificados: {e}')
        import traceback
        traceback.print_exc()
