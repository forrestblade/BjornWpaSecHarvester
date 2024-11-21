import os
import json
import logging
import requests
from pathlib import Path
from typing import Dict, Any, Set, Union
from urllib.request import Request, urlopen
from .security import SecurityManager

class SecureFileHandler:
    """Handles secure file operations for WPA-SEC harvesting."""
    
    def __init__(self):
        self.security = SecurityManager()
        self.logger = logging.getLogger(__name__)

    def download_wpa_sec_file(self, url: str, cookie_value: str, 
                             timeout: int = 30) -> Set[str]:
        """Download and process WPA-SEC file."""
        try:
            self.logger.info("Downloading WPA-SEC data...")
            headers = {'Cookie': f'key={cookie_value}'}
            req = Request(url, headers=headers)
            
            networks = set()
            with urlopen(req, timeout=timeout) as response:
                content = response.read().decode('utf-8', errors='ignore')
                
                for line in content.splitlines():
                    if ':' in line:
                        parts = line.strip().split(':')
                        if len(parts) >= 4:
                            networks.add(f"{parts[2]}:{parts[3]}")
                            
            self.logger.info(f"Downloaded {len(networks)} networks")
            return networks
            
        except Exception as e:
            self.logger.error(f"Download failed: {e}")
            raise

    def secure_write(self, filepath: Union[str, Path], 
                    content: str, mode: str = 'w') -> None:
        """Securely write content to file."""
        filepath = Path(filepath)
        temp_path = filepath.with_suffix('.tmp')
        
        try:
            with open(temp_path, mode, encoding='utf-8') as f:
                os.chmod(temp_path, 0o600)  # Owner read/write only
                f.write(content)
            os.replace(temp_path, filepath)
            
        except Exception as e:
            self.logger.error(f"File write failed: {e}")
            if temp_path.exists():
                os.unlink(temp_path)
            raise

    def secure_read(self, filepath: Union[str, Path]) -> str:
        """Securely read file content."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"File read failed: {e}")
            raise

    def secure_write_json(self, filepath: Union[str, Path], 
                         data: Dict[str, Any]) -> None:
        """Securely write JSON data."""
        try:
            content = json.dumps(data, indent=2)
            self.secure_write(filepath, content)
        except Exception as e:
            self.logger.error(f"JSON write failed: {e}")
            raise

    def secure_read_json(self, filepath: Union[str, Path]) -> Dict[str, Any]:
        """Securely read JSON data."""
        try:
            content = self.secure_read(filepath)
            return json.loads(content)
        except Exception as e:
            self.logger.error(f"JSON read failed: {e}")
            return {}

    def append_to_file(self, filepath: Union[str, Path], 
                      content: str) -> None:
        """Securely append content to file."""
        try:
            existing_content = self.secure_read(filepath) if Path(filepath).exists() else ""
            self.secure_write(filepath, existing_content + content)
        except Exception as e:
            self.logger.error(f"File append failed: {e}")
            raise
