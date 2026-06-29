"""
Encryption Utilities
Handles encryption/decryption of sensitive data like API keys.
"""
from cryptography.fernet import Fernet, InvalidToken
from flask import current_app


def get_cipher():
    """Get Fernet cipher using the configured encryption key."""
    key = current_app.config.get('ENCRYPTION_KEY', '')
    if not key:
        raise ValueError('ENCRYPTION_KEY not configured. Generate one with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"')
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_value(plaintext):
    """Encrypt a string value. Returns encrypted bytes as string."""
    if not plaintext:
        return ''
    cipher = get_cipher()
    return cipher.encrypt(plaintext.encode()).decode()


def decrypt_value(encrypted_text):
    """Decrypt an encrypted string. Returns plaintext."""
    if not encrypted_text:
        return ''
    try:
        cipher = get_cipher()
        return cipher.decrypt(encrypted_text.encode()).decode()
    except InvalidToken:
        return ''
