import pytest
import os
from pathlib import Path
from crypto_manager import CryptoManager
from cryptography.fernet import InvalidToken

def test_encryption_decryption() -> None:
    password = "master_password"
    manager = CryptoManager(password)
    original_text = "secret_data"
    
    encrypted = manager.encrypt(original_text)
    decrypted = manager.decrypt(encrypted)
    
    assert decrypted == original_text
    assert encrypted != original_text.encode()

def test_wrong_password_fails() -> None:
    password = "correct_password"
    manager = CryptoManager(password)
    encrypted = manager.encrypt("secret")
    
    wrong_manager = CryptoManager("wrong_password")
    with pytest.raises(InvalidToken):
        wrong_manager.decrypt(encrypted)

@pytest.fixture(autouse=True)
def cleanup_salt() -> None:
    salt_file = Path("salt.key")
    if salt_file.exists():
        os.remove(salt_file)
    yield
    if salt_file.exists():
        os.remove(salt_file)
