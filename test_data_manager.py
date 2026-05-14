import pytest
import os
from pathlib import Path
from data_manager import DataManager

def test_data_manager_crud() -> None:
    password = "test_password"
    dm = DataManager(password)
    
    # Test Add
    dm.add_credential("google.com", "user1", "pass1")
    assert len(dm.credentials) == 1
    assert dm.credentials[0]["website"] == "google.com"
    
    # Test persistence (load in a new manager)
    dm2 = DataManager(password)
    assert len(dm2.credentials) == 1
    assert dm2.credentials[0]["username"] == "user1"
    
    # Test Update
    dm.update_credential(0, "new.com", "new_user", "new_pass")
    assert dm.credentials[0]["website"] == "new.com"
    
    # Verify persistence of update
    dm3 = DataManager(password)
    assert dm3.credentials[0]["website"] == "new.com"

    # Test Remove
    dm.remove_credential(0)
    assert len(dm.credentials) == 0
    
    # Test persistence of removal
    dm4 = DataManager(password)
    assert len(dm4.credentials) == 0

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
