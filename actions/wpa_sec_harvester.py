from typing import Dict, Any, Optional
from pathlib import Path
import logging
from rich.console import Console
from BjornWpaSecHarvester.core.security import SecurityManager
from BjornWpaSecHarvester.core.file_handler import SecureFileHandler
from BjornWpaSecHarvester.core.network_manager import NetworkManager
from BjornWpaSecHarvester.utils.helpers import BjornHelper
class WpaSecHarvesterAction:
    """
    WPA-SEC Harvesting action for Bjorn.
    Integrates with Bjorn's display, stats, and network systems.
    """
    
    def __init__(self, shared_data: Dict[str, Any]):
        # Bjorn integration attributes
        self.b_class = "WpaSecHarvesting"
        self.b_module = "wpa_sec_harvesting"
        self.b_status = "wpa_sec_harvesting_action"
        self.b_port = 0
        self.b_parent = None
        
        # Core components
        self.shared_data = shared_data
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        
        # Initialize display with Bjorn helper
        BjornHelper.update_display_data(
            self.shared_data,
            status='startup',
            message='WPA-SEC Harvester initialized'
        )
        
        # Initialize managers
        self.security = SecurityManager()
        self.file_handler = SecureFileHandler()
        self.network_manager = NetworkManager()

    def execute(self, ip: Optional[str] = None, 
                port: Optional[int] = None, 
                row: Optional[Dict] = None, 
                status_key: Optional[str] = None) -> bool:
        """Execute the WPA-SEC harvesting action."""
        try:
            # Update display for harvest start
            BjornHelper.update_display_data(
                self.shared_data,
                status='harvesting',
                message='Starting WPA-SEC harvest'
            )

            # Download and process networks
            networks = self._harvest_networks()
            
            # Process each network
            for ssid, password in networks:
                # Format network data using helper
                network_data = BjornHelper.format_network_data(ssid, password)
                
                # Add network to system
                if self.network_manager.add_network(ssid, password):
                    # Update Bjorn's knowledge base
                    BjornHelper.update_netkb(self.shared_data, network_data)
                
                # Update display with progress
                BjornHelper.update_display_data(
                    self.shared_data,
                    status='processing',
                    message=f'Processing network: {ssid}',
                    network_count=len(networks)
                )

            # Final success update
            BjornHelper.update_display_data(
                self.shared_data,
                status='complete',
                message=f'Successfully harvested {len(networks)} networks',
                network_count=len(networks)
            )
            
            return True

        except Exception as e:
            error_msg = f"Harvest failed: {str(e)}"
            self.logger.error(error_msg)
            
            # Update display with error
            BjornHelper.update_display_data(
                self.shared_data,
                status='error',
                message=error_msg
            )
            
            return False

    def _harvest_networks(self) -> list:
        """Harvest networks from WPA-SEC."""
        try:
            BjornHelper.update_display_data(
                self.shared_data,
                status='downloading',
                message='Downloading WPA-SEC data...'
            )

            networks = self.file_handler.download_wpa_sec_file(
                self.shared_data.get('wpa_sec_url'),
                self.shared_data.get('wpa_sec_cookie')
            )

            # Update display with download results
            BjornHelper.update_display_data(
                self.shared_data,
                status='processing',
                message=f'Downloaded {len(networks)} networks',
                network_count=len(networks)
            )

            return networks

        except Exception as e:
            self.logger.error(f"Network harvesting failed: {e}")
            raise

    def _process_network(self, ssid: str, password: str) -> bool:
        """Process a single network."""
        try:
            # Validate network credentials
            validation = self.security.validate_network_credentials(ssid, password)
            if not validation['valid']:
                return False

            # Format network data
            network_data = BjornHelper.format_network_data(ssid, password)
            
            # Add network to system
            if self.network_manager.add_network(ssid, password):
                # Update Bjorn's knowledge base
                BjornHelper.update_netkb(self.shared_data, network_data)
                return True
                
            return False

        except Exception as e:
            self.logger.error(f"Failed to process network {ssid}: {e}")
            return False

