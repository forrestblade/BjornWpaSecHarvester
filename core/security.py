import os
import logging
import shlex
from pathlib import Path
from typing import Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class SecurityManager:
    """Handles security operations for WPA-SEC harvesting."""
    
    def __init__(self):
        self._setup_encryption()
        self.logger = logging.getLogger(__name__)

    def _setup_encryption(self) -> None:
        """Initialize encryption for sensitive data."""
        try:
            key = os.getenv('ENCRYPTION_KEY')
            if not key:
                key = self._generate_key()
            self.cipher_suite = Fernet(key.encode() if isinstance(key, str) else key)
        except Exception as e:
            self.logger.error(f"Encryption setup failed: {e}")
            raise

    def _generate_key(self) -> bytes:
        """Generate a new encryption key."""
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(os.urandom(32)))

    def validate_network_credentials(self, ssid: str, password: str) -> Dict[str, bool]:
        """Validate network credentials."""
        validation = {
            'valid': True,
            'password_length': True,
            'ssid_length': True,
            'ssid_chars': True,
            'password_complexity': True
        }
        
        # Password length (WPA2 requirements)
        if not (8 <= len(password) <= 63):
            validation['valid'] = False
            validation['password_length'] = False
            
        # SSID length
        if not ssid or len(ssid) > 32:
            validation['valid'] = False
            validation['ssid_length'] = False
            
        # SSID character validation
        if any(c in ssid for c in '\\/:*?"<>|'):
            validation['valid'] = False
            validation['ssid_chars'] = False
            
        # Basic password complexity
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_upper and has_lower and has_digit):
            validation['password_complexity'] = False
            
        return validation

    def secure_directory(self, directory: Path) -> None:
        """Secure a directory with appropriate permissions."""
        try:
            directory.mkdir(parents=True, exist_ok=True)
            os.chmod(directory, 0o700)  # Owner read/write/execute only
        except Exception as e:
            self.logger.error(f"Directory security setup failed: {e}")
            raise

    def encrypt_data(self, data: str) -> bytes:
        """Encrypt sensitive data."""
        return self.cipher_suite.encrypt(data.encode())

    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt sensitive data."""
        return self.cipher_suite.decrypt(encrypted_data).decode()

    def sanitize_command_input(self, input_str: str) -> str:
        """Sanitize input for command line usage."""
        return shlex.quote(input_str)
