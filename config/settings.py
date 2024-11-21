import os
from pathlib import Path
from typing import Dict, Any

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = DATA_DIR / "output"
INPUT_DIR = DATA_DIR / "input"
RESOURCE_DIR = BASE_DIR / "resources"

# WPA-SEC specific settings
WPA_SEC_SETTINGS = {
    'REQUIRED_PATHS': [
        OUTPUT_DIR / "networks",
        OUTPUT_DIR / "crackedpwd",
        OUTPUT_DIR / "scan_results",
        OUTPUT_DIR / "stats"
    ],
    
    'FILES': {
        'POTFILE': OUTPUT_DIR / "networks" / "wpa-sec.potfile",
        'CRACKED_FILE': OUTPUT_DIR / "crackedpwd" / "cracked.txt",
        'NETWORKS_FILE': OUTPUT_DIR / "networks" / "networks.txt",
        'STATS_FILE': OUTPUT_DIR / "stats" / "wpa_sec_stats.json"
    },
    
    'NETWORK': {
        'MIN_PASSWORD_LENGTH': 8,
        'MAX_PASSWORD_LENGTH': 63,
        'MAX_SSID_LENGTH': 32,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_ATTEMPTS': 3,
        'RETRY_DELAY': 2
    },
    
    'DISPLAY': {
        'UPDATE_INTERVAL': 1.0,  # seconds
        'PROGRESS_BAR': True,
        'SHOW_STATS': True
    },
    
    'WEB_INTERFACE': {
        'ENABLED': True,
        'PORT': 8000,
        'HOST': '0.0.0.0',
        'ROUTE_PREFIX': '/wpa-sec',
        'TEMPLATE_DIR': BASE_DIR / 'web' / 'templates',
        'STATIC_DIR': BASE_DIR / 'web' / 'static'
    }
}

# Bjorn integration settings
BJORN_SETTINGS = {
    'DISPLAY_THEMES': {
        'success': '✅',
        'error': '❌',
        'info': 'ℹ️',
        'warning': '⚠️'
    },
    'ICONS': {
        'startup': '⚔️',
        'search': '🔍',
        'process': '⚡',
        'download': '📥',
        'victory': '🏆',
        'error': '🛡️'
    }
}

def load_env_settings() -> Dict[str, str]:
    """Load environment variables."""
    required_vars = [
        'COOKIE_VALUE',
        'WPA_SEC_URL',
        'DISCORD_WEBHOOK_URL'
    ]
    
    env_settings = {}
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            env_settings[var] = value
        else:
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
    
    return env_settings

def get_settings() -> Dict[str, Any]:
    """Get complete settings dictionary."""
    return {
        'WPA_SEC': WPA_SEC_SETTINGS,
        'BJORN': BJORN_SETTINGS,
        'ENV': load_env_settings()
    }