#!/usr/bin/env python3

import os
import logging
from pathlib import Path
from BjornWpaSecHarvester.actions.wpa_sec_harvester import WpaSecHarvesterAction
from rich.console import Console

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def load_config():
    """Load configuration from environment variables."""
    required_vars = {
        'WPA_SEC_URL': 'https://wpa-sec.stanev.org/...',  # Your WPA-SEC URL
        'WPA_SEC_COOKIE': '',  # Your WPA-SEC cookie value
        'OUTPUT_DIR': str(Path(__file__).parent / 'data' / 'output')
    }
    
    # Check for missing environment variables
    missing_vars = [var for var, default in required_vars.items() 
                   if not os.getenv(var, default)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    return {
        'wpa_sec_url': os.getenv('WPA_SEC_URL'),
        'wpa_sec_cookie': os.getenv('WPA_SEC_COOKIE'),
        'output_dir': os.getenv('OUTPUT_DIR', required_vars['OUTPUT_DIR'])
    }

def main():
    try:
        # Load configuration
        config = load_config()
        
        # Initialize shared data
        shared_data = {
            'wpa_sec_url': config['wpa_sec_url'],
            'wpa_sec_cookie': config['wpa_sec_cookie'],
            'netkb': {},
            'stats': {},
            'paths': {
                'output': config['output_dir']
            }
        }
        
        # Initialize and run harvester
        harvester = WpaSecHarvesterAction(shared_data)
        success = harvester.execute()
        
        if success:
            logging.info("WPA-SEC harvest completed successfully!")
        else:
            logging.error("WPA-SEC harvest failed!")
            
    except Exception as e:
        logging.error(f"Error running WPA-SEC harvester: {e}")
        raise

if __name__ == "__main__":
    main() 