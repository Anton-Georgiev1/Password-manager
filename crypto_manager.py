import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CryptoManager:
    """Handles encryption and decryption using a master password."""

    ITERATIONS: int = 480_000

    def __init__(self, master_password: str, salt: bytes) -> None:
        self.salt = salt
        self.key = self._derive_key(master_password, self.salt)
        self.fernet = Fernet(self.key)

    @staticmethod
    def generate_salt() -> bytes:
        """Generates a new 16-byte random salt."""
        return os.urandom(16)

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derives a Fernet-compatible key from a password and salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.ITERATIONS,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    @staticmethod
    def hash_text(text: str) -> str:
        """Hashes a string using SHA-256."""
        digest = hashes.Hash(hashes.SHA256())
        digest.update(text.encode())
        return digest.finalize().hex()

    def encrypt(self, data: str) -> bytes:
        """Encrypts a string and returns bytes."""
        return self.fernet.encrypt(data.encode())

    def decrypt(self, encrypted_data: bytes) -> str:
        """Decrypts bytes and returns a string."""
        return self.fernet.decrypt(encrypted_data).decode()
