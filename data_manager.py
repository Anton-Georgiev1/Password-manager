import json
import os
from pathlib import Path
from typing import TypedDict
from crypto_manager import CryptoManager

class Credential(TypedDict):
    website: str
    username: str
    password: str

class DataManager:
    """Manages encrypted credential storage with embedded salt."""

    DATA_FILE: Path = Path("data.enc")
    SALT_SIZE: int = 16

    def __init__(self, master_password: str) -> None:
        self.master_password = master_password
        self.salt: bytes | None = None
        self.crypto: CryptoManager | None = None
        self.credentials: list[Credential] = self._load_data()

    def _load_data(self) -> list[Credential]:
        """Loads, extracts salt, and decrypts data from disk."""
        if not self.DATA_FILE.exists():
            return []
        
        try:
            file_data = self.DATA_FILE.read_bytes()
            if len(file_data) < self.SALT_SIZE:
                return []
            
            # Extract salt (first 16 bytes) and encrypted content
            self.salt = file_data[:self.SALT_SIZE]
            encrypted_content = file_data[self.SALT_SIZE:]
            
            self.crypto = CryptoManager(self.master_password, self.salt)
            decrypted_data = self.crypto.decrypt(encrypted_content)
            return json.loads(decrypted_data)
        except Exception:
            # Re-raise to let the app know login failed
            raise ValueError("Invalid password or corrupted data.")

    def save_data(self) -> None:
        """Encrypts data, prepends salt, and saves to disk."""
        # If new database, generate a salt
        if self.salt is None:
            self.salt = CryptoManager.generate_salt()
        
        if self.crypto is None or self.crypto.salt != self.salt:
            self.crypto = CryptoManager(self.master_password, self.salt)

        data_str = json.dumps(self.credentials)
        encrypted_content = self.crypto.encrypt(data_str)
        
        # Combined data: Salt + Ciphertext
        final_data = self.salt + encrypted_content
        
        # Atomic write
        tmp_file = self.DATA_FILE.with_suffix(".tmp")
        tmp_file.write_bytes(final_data)
        os.replace(tmp_file, self.DATA_FILE)

    def add_credential(self, website: str, username: str, password: str) -> None:
        self.credentials.append({
            "website": website,
            "username": username,
            "password": password
        })
        self.save_data()

    def remove_credential(self, index: int) -> None:
        if 0 <= index < len(self.credentials):
            self.credentials.pop(index)
            self.save_data()

    def update_credential(self, index: int, website: str, username: str, password: str) -> None:
        if 0 <= index < len(self.credentials):
            self.credentials[index] = {
                "website": website,
                "username": username,
                "password": password
            }
            self.save_data()
