"""
Encryption utilities (GDPR Article 32 compliance)
"""

from cryptography.fernet import Fernet


def generate_key() -> bytes:
    """Generate symmetric encryption key."""
    return Fernet.generate_key()


def get_cipher(key: bytes) -> Fernet:
    """Return Fernet cipher instance."""
    return Fernet(key)


def encrypt_data(key: bytes, data: bytes) -> bytes:
    """Encrypt bytes using Fernet."""
    cipher = get_cipher(key)
    return cipher.encrypt(data)


def decrypt_data(key: bytes, token: bytes) -> bytes:
    """Decrypt bytes using Fernet."""
    cipher = get_cipher(key)
    return cipher.decrypt(token)
