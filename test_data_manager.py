import pytest
import os
from pathlib import Path
from crypto_manager import CryptoManager
from data_manager import DataManager

@pytest.fixture
def crypto_manager() -> CryptoManager:
    return CryptoManager("test_password")

def test_data_manager_crud(crypto_manager: CryptoManager) -> None:
    dm = DataManager(crypto_manager)
    
    # Test Add
    dm.add_credential("google.com", "user1", "pass1")
    assert len(dm.credentials) == 1
    assert dm.credentials[0]["website"] == "google.com"
    
    # Test persistence (load in a new manager)
    dm2 = DataManager(crypto_manager)
    assert len(dm2.credentials) == 1
    assert dm2.credentials[0]["username"] == "user1"
    
    # Test Remove
    dm.remove_credential(0)
    assert len(dm.credentials) == 0
    
    # Test persistence of removal
    dm3 = DataManager(crypto_manager)
    assert len(dm3.credentials) == 0

def test_data_manager_update(crypto_manager: CryptoManager) -> None:
    dm = DataManager(crypto_manager)
    dm.add_credential("test.com", "user", "pass")
    
    dm.update_credential(0, "new.com", "new_user", "new_pass")
    assert dm.credentials[0]["website"] == "new.com"
    
    # Verify persistence
    dm2 = DataManager(crypto_manager)
    assert dm2.credentials[0]["website"] == "new.com"

@pytest.fixture(autouse=True)
def cleanup_files() -> None:
    files = [Path("data.enc"), Path("salt.key"), Path("data.tmp")]
    for f in files:
        if f.exists():
            os.remove(f)
    yield
    for f in files:
        if f.exists():
            os.remove(f)
