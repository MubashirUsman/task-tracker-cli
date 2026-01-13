import logging
import logging.handlers
import os
import json
import requests
from datetime import datetime


class RemoteLogHandler(logging.Handler):
    """Custom handler to send logs to a remote HTTP endpoint."""
    
    def __init__(self, remote_url, timeout=5):
        super().__init__()
        self.remote_url = remote_url
        self.timeout = timeout
    
    def emit(self, record):
        try:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': self.format(record),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }
            
            # Add extra fields if present
            if hasattr(record, 'request_id'):
                log_entry['request_id'] = record.request_id
            if hasattr(record, 'method'):
                log_entry['method'] = record.method
            if hasattr(record, 'path'):
                log_entry['path'] = record.path
            if hasattr(record, 'status_code'):
                log_entry['status_code'] = record.status_code
            
            requests.post(
                self.remote_url,
                json=log_entry,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
        except Exception:
            # Don't let logging failures crash the app
            self.handleError(record)


def setup_logging(app):
    """
    Configure logging based on environment variables.
    
    Environment variables:
    - LOG_LEVEL: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)
    - LOG_OUTPUT: 'stdout' or 'remote' (default: stdout)
    - LOG_REMOTE_URL: URL for remote logging (required if LOG_OUTPUT=remote)
    - LOG_FORMAT: 'json' or 'text' (default: text)
    """
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    log_output = os.environ.get('LOG_OUTPUT', 'stdout').lower()
    log_format = os.environ.get('LOG_FORMAT', 'text').lower()
    remote_url = os.environ.get('LOG_REMOTE_URL', '')
    
    # Create logger
    logger = logging.getLogger('task_tracker')
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Clear existing handlers
    logger.handlers = []
    
    # Define formatters
    if log_format == 'json':
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Configure handler based on output type
    if log_output == 'remote' and remote_url:
        handler = RemoteLogHandler(remote_url)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        # Also add stdout as fallback
        stdout_handler = logging.StreamHandler()
        stdout_handler.setFormatter(formatter)
        stdout_handler.setLevel(logging.WARNING)  # Only warnings+ to stdout when remote
        logger.addHandler(stdout_handler)
    else:
        # Default to stdout
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    # Attach logger to app
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
    
    return logger


class JsonFormatter(logging.Formatter):
    """Format log records as JSON."""
    
    def format(self, record):
        log_dict = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_dict['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key in ['request_id', 'method', 'path', 'status_code', 'duration_ms']:
            if hasattr(record, key):
                log_dict[key] = getattr(record, key)
        
        return json.dumps(log_dict)


def get_logger():
    """Get the configured logger instance."""
    return logging.getLogger('task_tracker')
