# 🛡️ Secure Vault - Your Private Password Manager

![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)
![Security](https://img.shields.io/badge/security-AES--256-green.svg)
![UI](https://img.shields.io/badge/UI-CustomTkinter-blueviolet.svg)

**Secure Vault** is a lightweight, modern, and highly secure password manager built with Python. Designed with a security-first mindset, it ensures that your digital identity remains private and accessible only to you. No cloud, no third parties—just your data, encrypted on your machine.

---

## Features

### Uncompromising Security
*   **Military-Grade Encryption:** Uses `AES-256` (via Fernet) to protect your credentials.
*   **Advanced Key Derivation:** Your master password is never stored. We use `PBKDF2` with `SHA-256` and 480,000 iterations to derive your encryption key.
*   **Embedded Salt Management:** Unlike many managers, we embed a 16-byte random salt directly into your encrypted data file for maximum portability and security.
*   **Atomic Writes:** Prevents data corruption by ensuring your database is updated safely using temporary swap files.

### Modern & Intuitive UI
*   **CustomTkinter Interface:** A sleek, professional design that supports system-wide dark and light modes.
*   **Tabbed Navigation:** Effortlessly switch between viewing your passwords, adding new ones, and generating secure keys.
*   **Responsive Management:** Add, remove, and **edit** your credentials with a few clicks.

### Secure Password Generator
*   **Customizable Complexity:** Generate unique passwords using a mix of uppercase letters, lowercase letters, numbers, and special symbols.
*   **Adjustable Length:** Fine-tune your security requirements with a length slider (up to 64 characters).
*   **Instant Clipboard:** Copy your newly generated password with a single click.

---

## Getting Started

### Prerequisites
*   **Python 3.12+**
*   **Libraries:** `customtkinter`, `cryptography`

### Installation
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/secure-vault.git
    cd secure-vault
    ```
2.  **Install dependencies:**
    ```bash
    pip install customtkinter cryptography
    ```

### Usage
Run the application:
```bash
python Password-manager.py
```
Upon the first launch, you will set your **Master Password**. *Caution: If you lose this password, your data cannot be recovered.*

---

## Technology Stack
*   **GUI:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for a modern, native feel.
*   **Encryption:** [Cryptography](https://cryptography.io/) for industry-standard security primitives.
*   **Persistence:** Encrypted JSON-based flat file storage.
*   **Testing:** Fully covered by `pytest` for reliability.

---

## Project Structure
*   `Password-manager.py`: Main entry point and GUI logic.
*   `crypto_manager.py`: Core encryption and key derivation services.
*   `data_manager.py`: Secure data persistence and CRUD operations.
*   `password_generator.py`: Secure random password generation logic.
*   `test_*.py`: Comprehensive unit testing suite.

---

## Security Note
This project is designed for local-first privacy. Your `data.enc` file contains all your credentials in an encrypted state. Keep it safe, and never share your master password.

---

## Contributing
Contributions are welcome! If you find a bug or have a feature request, please open an issue or submit a pull request.

---

## License
This project is licensed under the MIT License.
