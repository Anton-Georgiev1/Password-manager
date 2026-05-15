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
        Ensures at least one character from each selected category is present.
        """
        if settings.length < 1:
            raise ValueError("Password length must be at least 1.")

        pools: list[str] = []
        if settings.use_upper:
            pools.append(string.ascii_uppercase)
        if settings.use_lower:
            pools.append(string.ascii_lowercase)
        if settings.use_digits:
            pools.append(string.digits)
        
        # Combined symbol pool (All + Custom)
        symbol_pool = ""
        if settings.use_special:
            symbol_pool += string.punctuation
        if settings.custom_symbols:
            for char in settings.custom_symbols:
                if char not in symbol_pool:
                    symbol_pool += char
        
        if symbol_pool:
            pools.append(symbol_pool)

        if not pools:
            raise ValueError("At least one character type must be selected.")

        if settings.length < len(pools):
            raise ValueError(f"Password length too short to include all required types (Minimum: {len(pools)})")

        # 1. Start with one character from each required pool to guarantee presence
        password_chars = [secrets.choice(pool) for pool in pools]

        # 2. Fill the rest of the length from the combined pool
        all_chars = "".join(pools)
        password_chars += [secrets.choice(all_chars) for _ in range(settings.length - len(pools))]

        # 3. Shuffle the result to ensure the required characters aren't always at the start
        secrets.SystemRandom().shuffle(password_chars)

        return "".join(password_chars)
