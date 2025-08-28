"""
Configuration management module
"""

import os
import sys
from typing import Dict, Any, List
from dotenv import load_dotenv
import pytz


def load_settings() -> Dict[str, Any]:
    """
    Load and validate configuration settings from environment variables.
    
    Returns:
        Dict[str, Any]: Configuration dictionary with validated settings
    """
    # Load .env file if it exists
    load_dotenv()
    
    # Required settings
    dingtalk_token = os.getenv('DINGTALK_ACCESS_TOKEN')
    if not dingtalk_token:
        raise ValueError("DINGTALK_ACCESS_TOKEN is required")
    
    # Parse Nitter URLs
    nitter_urls_str = os.getenv('NITTER_BASE_URLS', 'https://nitter.poast.org')
    nitter_urls = [url.strip() for url in nitter_urls_str.split(',')]
    
    # Parse polling interval
    try:
        poll_seconds = int(os.getenv('X_POLL_SECONDS', '60'))
        if poll_seconds < 10:
            raise ValueError("X_POLL_SECONDS must be at least 10 seconds")
    except ValueError as e:
        raise ValueError(f"Invalid X_POLL_SECONDS: {e}")
    
    # Parse timeout values
    try:
        request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
        max_retries = int(os.getenv('MAX_RETRIES', '3'))
        retry_delay = int(os.getenv('RETRY_DELAY', '5'))
    except ValueError as e:
        raise ValueError(f"Invalid timeout configuration: {e}")
    
    # Parse boolean values
    on_first_run_push_all = os.getenv('ON_FIRST_RUN_PUSH_ALL', 'false').lower() == 'true'
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Validate timezone
    timezone_str = os.getenv('TIMEZONE', 'Asia/Shanghai')
    try:
        pytz.timezone(timezone_str)
    except pytz.UnknownTimeZoneError:
        raise ValueError(f"Invalid timezone: {timezone_str}")
    
    # Create directories if they don't exist
    state_dir = os.getenv('STATE_DIR', './data/state')
    log_dir = os.getenv('LOG_DIR', './data/logs')
    
    os.makedirs(state_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)
    
    config = {
        'dingtalk': {
            'access_token': dingtalk_token
        },
        'twitter': {
            'username': os.getenv('X_USERNAME', 'elonmusk'),
            'poll_seconds': poll_seconds
        },
        'nitter': {
            'base_urls': nitter_urls
        },
        'xtracker': {
            'url': os.getenv('XTRACKER_URL', 'https://www.xtracker.io/api/users?stats=true&platform=X')
        },
        'paths': {
            'state_dir': state_dir,
            'log_dir': log_dir
        },
        'timezone': timezone_str,
        'on_first_run_push_all': on_first_run_push_all,
        'request_timeout': request_timeout,
        'max_retries': max_retries,
        'retry_delay': retry_delay,
        'debug': debug,
        'log_level': os.getenv('LOG_LEVEL', 'INFO' if not debug else 'DEBUG')
    }
    
    return config


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate the configuration settings.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary to validate
        
    Returns:
        bool: True if configuration is valid
    """
    required_keys = [
        'dingtalk.access_token',
        'twitter.username',
        'twitter.poll_seconds',
        'nitter.base_urls',
        'xtracker.url',
        'paths.state_dir',
        'paths.log_dir'
    ]
    
    for key in required_keys:
        keys = key.split('.')
        value = config
        for k in keys:
            if k not in value:
                print(f"Missing configuration: {key}")
                return False
            value = value[k]
    
    # Validate specific values
    if not config['dingtalk']['access_token']:
        print("DINGTALK_ACCESS_TOKEN cannot be empty")
        return False
    
    if not config['twitter']['username']:
        print("X_USERNAME cannot be empty")
        return False
    
    if config['twitter']['poll_seconds'] < 10:
        print("X_POLL_SECONDS must be at least 10 seconds")
        return False
    
    if not config['nitter']['base_urls']:
        print("NITTER_BASE_URLS cannot be empty")
        return False
    
    return True


def print_config_help():
    """Print configuration help information."""
    help_text = """
Configuration Help:

Required Environment Variables:
- DINGTALK_ACCESS_TOKEN: DingTalk webhook access token
- X_USERNAME: Twitter/X username to monitor (without @)

Optional Environment Variables:
- X_POLL_SECONDS: Polling interval in seconds (default: 60)
- NITTER_BASE_URLS: Comma-separated Nitter mirror URLs
- XTRACKER_URL: XTracker API endpoint URL
- TIMEZONE: Timezone for scheduling (default: Asia/Shanghai)
- STATE_DIR: Directory for state files (default: ./data/state)
- LOG_DIR: Directory for log files (default: ./data/logs)
- ON_FIRST_RUN_PUSH_ALL: Push all tweets on first run (default: false)
- REQUEST_TIMEOUT: HTTP request timeout in seconds (default: 30)
- MAX_RETRIES: Maximum retry attempts (default: 3)
- RETRY_DELAY: Delay between retries in seconds (default: 5)
- DEBUG: Enable debug mode (default: false)
- LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

Example .env file:
```
DINGTALK_ACCESS_TOKEN=your-token-here
X_USERNAME=elonmusk
X_POLL_SECONDS=60
NITTER_BASE_URLS=https://nitter.poast.org,https://nitter.privacydev.net
```
"""
    print(help_text)


if __name__ == "__main__":
    try:
        config = load_settings()
        if validate_config(config):
            print("Configuration is valid!")
            print(f"Monitoring user: @{config['twitter']['username']}")
            print(f"Polling interval: {config['twitter']['poll_seconds']}s")
            print(f"Nitter URLs: {len(config['nitter']['base_urls'])} configured")
        else:
            print("Configuration validation failed!")
            sys.exit(1)
    except ValueError as e:
        print(f"Configuration error: {e}")
        print_config_help()
        sys.exit(1)