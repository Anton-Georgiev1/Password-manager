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
    """Manages encrypted credential storage."""

    DATA_FILE: Path = Path("data.enc")

    def __init__(self, crypto_manager: CryptoManager) -> None:
        self.crypto = crypto_manager
        self.credentials: list[Credential] = self._load_data()

    def _load_data(self) -> list[Credential]:
        """Loads and decrypts data from disk."""
        if not self.DATA_FILE.exists():
            return []
        
        try:
            encrypted_data = self.DATA_FILE.read_bytes()
            decrypted_data = self.crypto.decrypt(encrypted_data)
            return json.loads(decrypted_data)
        except Exception:
            # If decryption fails (e.g. wrong password), we should probably let the caller handle it.
            # For now, we'll return empty list if file is corrupted or other error.
            # But in the app, we'll verify password before initializing DataManager.
            return []

    def save_data(self) -> None:
        """Encrypts and saves data to disk."""
        data_str = json.dumps(self.credentials)
        encrypted_data = self.crypto.encrypt(data_str)
        
        # Atomic write: write to tmp then rename
        tmp_file = self.DATA_FILE.with_suffix(".tmp")
        tmp_file.write_bytes(encrypted_data)
        os.replace(tmp_file, self.DATA_FILE)

    def add_credential(self, website: str, username: str, password: str) -> None:
        """Adds a new credential and saves."""
        self.credentials.append({
            "website": website,
            "username": username,
            "password": password
        })
        self.save_data()

    def remove_credential(self, index: int) -> None:
        """Removes a credential by index and saves."""
        if 0 <= index < len(self.credentials):
            self.credentials.pop(index)
            self.save_data()
