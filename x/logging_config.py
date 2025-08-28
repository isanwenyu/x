"""
Logging configuration module
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional


def get_logger(name: str, log_dir: Optional[str] = None, log_level: str = "INFO") -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name (str): Logger name
        log_dir (Optional[str]): Directory for log files. If None, logs to console only.
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Set logging level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if log_dir is provided
    if log_dir:
        try:
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"x_monitor_{datetime.now().strftime('%Y%m%d')}.log")
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.warning(f"Could not create file handler: {e}")
    
    return logger


def setup_global_logging(log_dir: Optional[str] = None, log_level: str = "INFO"):
    """
    Setup global logging configuration.
    
    Args:
        log_dir (Optional[str]): Directory for log files
        log_level (str): Logging level
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler
    if log_dir:
        try:
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"x_monitor_{datetime.now().strftime('%Y%m%d')}.log")
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            
        except Exception as e:
            root_logger.warning(f"Could not create file handler: {e}")
    
    # Set third-party loggers to WARNING level to reduce noise
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)


class ColoredFormatter(logging.Formatter):
    """Colored log formatter for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def get_colored_logger(name: str, log_dir: Optional[str] = None, log_level: str = "INFO") -> logging.Logger:
    """
    Get a colored logger for console output.
    
    Args:
        name (str): Logger name
        log_dir (Optional[str]): Directory for log files
        log_level (str): Logging level
        
    Returns:
        logging.Logger: Configured logger with colored output
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    # Use colored formatter
    if os.name != 'nt':  # Not Windows
        formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (no colors for file)
    if log_dir:
        try:
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"x_monitor_{datetime.now().strftime('%Y%m%d')}.log")
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.warning(f"Could not create file handler: {e}")
    
    return logger


# Test function
def test_logging():
    """Test logging configuration"""
    print("Testing logging configuration...")
    
    # Test basic logger
    logger = get_logger("test_logger")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test colored logger
    colored_logger = get_colored_logger("test_colored")
    colored_logger.debug("This is a debug message")
    colored_logger.info("This is an info message")
    colored_logger.warning("This is a warning message")
    colored_logger.error("This is an error message")
    
    # Test with file logging
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        file_logger = get_logger("test_file", log_dir=temp_dir, log_level="DEBUG")
        file_logger.debug("This debug message should appear in log file")
        file_logger.info("This info message should appear in log file")
        
        # Check if log file was created
        log_files = [f for f in os.listdir(temp_dir) if f.endswith('.log')]
        if log_files:
            print(f"Log file created: {log_files[0]}")
            with open(os.path.join(temp_dir, log_files[0]), 'r') as f:
                print("Log file contents:")
                print(f.read())
        else:
            print("No log files created")


if __name__ == "__main__":
    test_logging()