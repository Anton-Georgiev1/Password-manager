import pytest
from password_generator import PasswordGenerator, PasswordSettings

def test_generate_password_length() -> None:
    settings = PasswordSettings(length=20)
    password = PasswordGenerator.generate(settings)
    assert len(password) == 20

def test_generate_password_types() -> None:
    # Test digits only
    settings = PasswordSettings(length=10, use_upper=False, use_lower=False, use_digits=True, use_special=False)
    password = PasswordGenerator.generate(settings)
    assert password.isdigit()

    # Test uppercase only
    settings = PasswordSettings(length=10, use_upper=True, use_lower=False, use_digits=False, use_special=False)
    password = PasswordGenerator.generate(settings)
    assert password.isupper()

def test_generate_password_invalid_length() -> None:
    settings = PasswordSettings(length=0)
    with pytest.raises(ValueError, match="Password length must be at least 1."):
        PasswordGenerator.generate(settings)

def test_generate_password_no_types() -> None:
    settings = PasswordSettings(use_upper=False, use_lower=False, use_digits=False, use_special=False)
    with pytest.raises(ValueError, match="At least one character type must be selected."):
        PasswordGenerator.generate(settings)
