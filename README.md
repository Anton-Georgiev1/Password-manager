# Secure Password Manager

A modern, high-security password manager built with Python and CustomTkinter. This application features robust AES-256 encryption, a vertical simplified login system, and an emergency recovery architecture.

## 🚀 Key Features

### 1. Smart Login System
- **Compact UI:** A streamlined 350px height login screen for focused access.
- **Caps Lock Indicator:** Real-time visual warning (⚠️) if Caps Lock is active.
- **Language Layout Detection:** Detects non-English keyboard layouts to prevent accidental login failures.
- **Integrated Show Password:** Toggle visibility directly within the entry field using a discrete eye icon.

### 2. Emergency Recovery Key System
- **24-Character Recovery Key:** Automatically generated during account creation or password resets.
- **Cryptographic Fingerprinting:** Uses SHA-256 hashing to verify recovery keys without storing the key itself.
- **Encrypted Backup:** Your master password is encrypted using the recovery key as a secondary safety net.
- **Auto-Sync:** A new recovery key is generated and displayed every time you change or recover your master password.

### 3. Master Password Management
- **Direct Change/Recovery:** Perform master password updates or emergency resets directly from the login screen.
- **Atomic Operations:** Ensures data integrity by using temp files and atomic replacement during encryption/decryption cycles.

### 4. Advanced Password Generator
- **Guaranteed Presence:** Ensures at least one character from each selected category (Upper, Lower, Digits, Symbols) is present.
- **Custom Symbol Support:** Input specific symbols you want to include, or enable "All Symbols" for full punctuation.
- **Secure Shuffling:** Uses `secrets.SystemRandom` for high-entropy shuffling of generated strings.

## 🛠 Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd "Password manager"
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install customtkinter cryptography
   ```

## 🖥 Usage

Run the main application:
```bash
python Password-manager.py
```

### <span style="color:red">**Important Security Note**</span>
<span style="color:red">**Save your Recovery Key!** In case you forget your Master Password, the 24-character key is the **only** way to recover your vault. If both are lost, your data cannot be decrypted.</span>

## 🔒 Security Architecture
- **Encryption:** AES-256 (Fernet) with PBKDF2HMAC key derivation.
- **Salt:** Unique 16-byte salt per file to prevent rainbow table attacks.
- **Hashing:** SHA-256 for integrity checks and recovery fingerprinting.
- **Zero-Trust:** All decryption happens in RAM; unencrypted data is never written to disk.

## 📄 License
This project is for educational/personal use. Please ensure you follow security best practices when managing sensitive credentials.
