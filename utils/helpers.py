import time
import logging
from typing import Dict, Any, Optional
from pathlib import Path

class BjornHelper:
    """
    Helper functions for integrating WPA-SEC Harvester with Bjorn's systems.
    Handles data formatting, knowledge base updates, and display messages.
    """
    
    @staticmethod
    def format_network_data(ssid: str, password: str) -> Dict[str, str]:
        """
        Format network data to match Bjorn's expected structure.
        
        Args:
            ssid: Network SSID
            password: Network password
            
        Returns:
            Formatted network data dictionary
        """
        return {
            'ssid': ssid,
            'password': password,
            'timestamp': str(int(time.time())),
            'source': 'wpa_sec_harvester',
            'action_type': 'harvest',
            'status': 'discovered'
        }

    @staticmethod
    def update_netkb(shared_data: Dict[str, Any], 
                     network_data: Dict[str, str]) -> None:
        """
        Update Bjorn's network knowledge base with new network data.
        
        Args:
            shared_data: Bjorn's shared data dictionary
            network_data: Network information to add
        """
        try:
            netkb = shared_data.get('netkb', {})
            ssid = network_data['ssid']
            
            if ssid not in netkb:
                # New network entry
                netkb[ssid] = {
                    'first_seen': network_data['timestamp'],
                    'last_updated': network_data['timestamp'],
                    'source': network_data['source'],
                    'status': network_data['status'],
                    'action_history': [{
                        'action': 'discovered',
                        'timestamp': network_data['timestamp'],
                        'source': 'wpa_sec_harvester'
                    }]
                }
            else:
                # Update existing network
                netkb[ssid].update({
                    'last_updated': network_data['timestamp'],
                    'status': 'updated'
                })
                netkb[ssid]['action_history'].append({
                    'action': 'updated',
                    'timestamp': network_data['timestamp'],
                    'source': 'wpa_sec_harvester'
                })
                
            shared_data['netkb'] = netkb
            
        except Exception as e:
            logging.error(f"Failed to update network knowledge base: {e}")

    @staticmethod
    def update_display_data(shared_data: Dict[str, Any], 
                          status: str, 
                          message: str,
                          network_count: Optional[int] = None) -> None:
        """
        Update Bjorn's display with current harvester status.
        
        Args:
            shared_data: Bjorn's shared data dictionary
            status: Current status
            message: Status message
            network_count: Number of networks (optional)
        """
        try:
            display_data = {
                'module': 'WPA-SEC Harvester',
                'status': status,
                'message': message,
                'icon': BjornHelper._get_status_icon(status),
                'stats': {
                    'networks_found': network_count if network_count else 
                                    shared_data.get('stats', {}).get('total_networks_found', 0)
                }
            }
            
            shared_data['display'] = display_data
            
        except Exception as e:
            logging.error(f"Failed to update display data: {e}")

    @staticmethod
    def _get_status_icon(status: str) -> str:
        """Get appropriate icon for status."""
        icons = {
            'harvesting': '🔍',
            'success': '✅',
            'error': '❌',
            'processing': '⚡',
            'complete': '🏆'
        }
        return icons.get(status, 'ℹ️')