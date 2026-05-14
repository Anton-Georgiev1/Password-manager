import pytest
import os
from pathlib import Path
from crypto_manager import CryptoManager
from cryptography.fernet import InvalidToken

def test_encryption_decryption() -> None:
    password = "master_password"
    salt = CryptoManager.generate_salt()
    manager = CryptoManager(password, salt)
    original_text = "secret_data"
    
    encrypted = manager.encrypt(original_text)
    decrypted = manager.decrypt(encrypted)
    
    assert decrypted == original_text
    assert encrypted != original_text.encode()

def test_wrong_password_fails() -> None:
    password = "correct_password"
    salt = CryptoManager.generate_salt()
    manager = CryptoManager(password, salt)
    encrypted = manager.encrypt("secret")
    
    wrong_manager = CryptoManager("wrong_password", salt)
    with pytest.raises(InvalidToken):
        wrong_manager.decrypt(encrypted)
