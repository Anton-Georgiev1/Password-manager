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
    RECOVERY_HASH_FILE: Path = Path("recovery.hash")
    RECOVERY_DATA_FILE: Path = Path("recovery.enc")
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

    def change_password(self, new_password: str) -> None:
        """Changes the master password and re-encrypts everything."""
        self.master_password = new_password
        # Force re-creation of crypto with new password
        self.crypto = CryptoManager(self.master_password, self.salt or CryptoManager.generate_salt())
        self.save_data()
        
        # Update recovery file if it exists
        if self.RECOVERY_HASH_FILE.exists():
            # We don't have the recovery key here, so we can't update recovery.enc
            # The app should probably handle this by asking for the recovery key 
            # or we just leave it for now.
            # Actually, the best way is to regenerate the recovery info when password changes
            # but we need the recovery key for that.
            pass

    def setup_recovery(self, recovery_key: str) -> None:
        """Sets up recovery by saving a hash and an encrypted master password."""
        # 1. Save hash of recovery key
        recovery_hash = CryptoManager.hash_text(recovery_key)
        self.RECOVERY_HASH_FILE.write_text(recovery_hash)
        
        # 2. Encrypt master password with recovery key
        recovery_salt = CryptoManager.generate_salt()
        recovery_crypto = CryptoManager(recovery_key, recovery_salt)
        encrypted_master = recovery_crypto.encrypt(self.master_password)
        
        # Store as Salt + Encrypted Master Password
        self.RECOVERY_DATA_FILE.write_bytes(recovery_salt + encrypted_master)

    @classmethod
    def verify_recovery_key(cls, recovery_key: str) -> bool:
        """Verifies if the recovery key matches the stored hash."""
        if not cls.RECOVERY_HASH_FILE.exists():
            return False
        stored_hash = cls.RECOVERY_HASH_FILE.read_text().strip()
        return CryptoManager.hash_text(recovery_key) == stored_hash

    @classmethod
    def recover_master_password(cls, recovery_key: str) -> str:
        """Uses recovery key to decrypt the stored master password."""
        if not cls.RECOVERY_DATA_FILE.exists():
            raise ValueError("Recovery data not found.")
        
        file_data = cls.RECOVERY_DATA_FILE.read_bytes()
        salt = file_data[:cls.SALT_SIZE]
        encrypted_content = file_data[cls.SALT_SIZE:]
        
        recovery_crypto = CryptoManager(recovery_key, salt)
        return recovery_crypto.decrypt(encrypted_content)

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
