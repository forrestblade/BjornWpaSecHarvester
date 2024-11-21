from typing import Dict, Any
import time
import json
from pathlib import Path
import logging

class StatsManager:
    """Manages statistics for WPA-SEC Harvester."""
    
    def __init__(self, shared_data: Dict[str, Any]):
        self.shared_data = shared_data
        self.logger = logging.getLogger(__name__)
        self.stats_file = Path('data/output/stats/wpa_sec_stats.json')
        self.stats = self._load_stats()

    def update_stats(self, new_stats: Dict[str, Any]) -> None:
        """Update statistics with new data."""
        try:
            self.stats.update(new_stats)
            self._save_stats()
            self.shared_data.update({'stats': self.stats})
        except Exception as e:
            self.logger.error(f"Failed to update stats: {e}")

    def get_current_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        return self.stats

    def get_timestamp(self) -> float:
        """Get current timestamp."""
        return time.time()

    def _load_stats(self) -> Dict[str, Any]:
        """Load statistics from file."""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load stats: {e}")
        
        return self._get_default_stats()

    def _save_stats(self) -> None:
        """Save statistics to file."""
        try:
            self.stats_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save stats: {e}")

    def _get_default_stats(self) -> Dict[str, Any]:
        """Get default statistics structure."""
        return {
            'total_networks_found': 0,
            'successful_harvests': 0,
            'failed_attempts': 0,
            'last_harvest_time': None,
            'last_successful_harvest': None,
            'last_error': None,
            'last_error_time': None,
            'harvest_history': []
        }

    def add_to_history(self, entry: Dict[str, Any]) -> None:
        """Add entry to harvest history."""
        try:
            history = self.stats.get('harvest_history', [])
            history.append({
                'timestamp': self.get_timestamp(),
                'data': entry
            })
            
            # Keep only last 100 entries
            if len(history) > 100:
                history = history[-100:]
                
            self.stats['harvest_history'] = history
            self._save_stats()
            
        except Exception as e:
            self.logger.error(f"Failed to add history entry: {e}")
