import subprocess
import logging
import time
from typing import Optional, Dict, List
from pathlib import Path
from .security import SecurityManager

class NetworkManager:
    """Manages network operations for WPA-SEC harvesting."""
    
    def __init__(self):
        self.security = SecurityManager()
        self.logger = logging.getLogger(__name__)
        self.wifi_device = self._get_wifi_device()

    def _get_wifi_device(self) -> Optional[str]:
        """Get primary WiFi device name."""
        try:
            result = subprocess.run(
                ["iwconfig"],
                capture_output=True,
                text=True,
                check=True
            )
            
            for line in result.stdout.splitlines():
                if "IEEE 802.11" in line:
                    return line.split()[0]
            
            self.logger.error("No WiFi device found")
            return None
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect WiFi device: {e}")
            return None

    def check_network_exists(self, ssid: str) -> bool:
        """Check if network exists in Bjorn's database."""
        try:
            result = subprocess.run(
                ["nmcli", "-t", "-f", "NAME", "connection", "show"],
                capture_output=True,
                text=True,
                check=True
            )
            return ssid in result.stdout
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Network check failed: {e}")
            return False

    def add_network(self, ssid: str, password: str) -> bool:
        """Add network to Bjorn's database."""
        if not self.wifi_device:
            self.logger.error("No WiFi device available")
            return False

        safe_ssid = self.security.sanitize_command_input(ssid)
        safe_password = self.security.sanitize_command_input(password)

        try:
            if self.check_network_exists(safe_ssid):
                return self._update_network(safe_ssid, safe_password)
            
            command = [
                "nmcli", "device", "wifi", "connect", safe_ssid,
                "password", safe_password
            ]
            
            subprocess.run(command, check=True, capture_output=True)
            self.logger.info(f"Successfully added network: {safe_ssid}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to add network {safe_ssid}: {e}")
            return False

    def _update_network(self, ssid: str, password: str) -> bool:
        """Update existing network in Bjorn's database."""
        try:
            command = [
                "nmcli", "connection", "modify", ssid,
                "wifi-sec.psk", password
            ]
            
            subprocess.run(command, check=True, capture_output=True)
            self.logger.info(f"Successfully updated network: {ssid}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to update network {ssid}: {e}")
            return False
