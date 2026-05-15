import secrets
import string
from dataclasses import dataclass

@dataclass(frozen=True)
class PasswordSettings:
    """Settings for password generation."""
    length: int = 16
    use_upper: bool = True
    use_lower: bool = True
    use_digits: bool = True
    use_special: bool = True
    custom_symbols: str = ""

class PasswordGenerator:
    """Secure password generator."""

    @staticmethod
    def generate(settings: PasswordSettings) -> str:
        """
        Generates a secure random password based on provided settings.
        
        Args:
            settings: Configuration for password complexity and length.
            
        Returns:
            A secure random string.
            
        Raises:
            ValueError: If no character types are selected or length is less than 1.
        """
        if settings.length < 1:
            raise ValueError("Password length must be at least 1.")

        chars = ""
        if settings.use_upper:
            chars += string.ascii_uppercase
        if settings.use_lower:
            chars += string.ascii_lowercase
        if settings.use_digits:
            chars += string.digits
        if settings.use_special:
            chars += string.punctuation
        
        if settings.custom_symbols:
            # Add custom symbols, avoiding duplicates if some were already added by use_special
            for char in settings.custom_symbols:
                if char not in chars:
                    chars += char

        if not chars:
            raise ValueError("At least one character type must be selected.")

        return "".join(secrets.choice(chars) for _ in range(settings.length))
