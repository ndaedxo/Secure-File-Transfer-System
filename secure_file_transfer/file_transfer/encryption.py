# secure_file_transfer\file_transfer\encryption.py
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

class FileEncryptor:
    @staticmethod
    def generate_key(password: str, salt: bytes = None) -> bytes:
        """
        Generate a secure encryption key from a password
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt

    @staticmethod
    def encrypt_file(file, password: str) -> dict:
        """
        Encrypt a file with a user-provided password
        """
        # Generate a unique key and salt
        key, salt = FileEncryptor.generate_key(password)
        
        # Create Fernet cipher
        fernet = Fernet(key)
        
        # Read file contents
        file_contents = file.read()
        
        # Encrypt the file contents
        encrypted_contents = fernet.encrypt(file_contents)
        
        return {
            'encrypted_file': encrypted_contents,
            'salt': base64.b64encode(salt).decode(),
        }

    @staticmethod
    def decrypt_file(encrypted_file, password: str, salt: bytes) -> bytes:
        """
        Decrypt a file using the password and salt
        """
        # Regenerate the key
        key, _ = FileEncryptor.generate_key(password, salt)
        
        # Create Fernet cipher
        fernet = Fernet(key)
        
        # Decrypt the file contents
        decrypted_contents = fernet.decrypt(encrypted_file)
        
        return decrypted_contents