import base64
import os
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CryptoManager:
    """Handles encryption and decryption using a master password."""

    SALT_FILE: Path = Path("salt.key")
    ITERATIONS: int = 480_000

    def __init__(self, master_password: str) -> None:
        self.salt = self._get_or_create_salt()
        self.key = self._derive_key(master_password, self.salt)
        self.fernet = Fernet(self.key)

    def _get_or_create_salt(self) -> bytes:
        """Retrieves existing salt or creates a new one."""
        if self.SALT_FILE.exists():
            return self.SALT_FILE.read_bytes()
        
        salt = os.urandom(16)
        self.SALT_FILE.write_bytes(salt)
        return salt

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derives a Fernet-compatible key from a password and salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.ITERATIONS,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def encrypt(self, data: str) -> bytes:
        """Encrypts a string and returns bytes."""
        return self.fernet.encrypt(data.encode())

    def decrypt(self, encrypted_data: bytes) -> str:
        """Decrypts bytes and returns a string."""
        return self.fernet.decrypt(encrypted_data).decode()
