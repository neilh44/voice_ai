# app/core/logging.py
import logging
import sys
import json
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os

from app.core.config import settings

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logger names for different components
LOGGERS = {
    "app": "voice_ai.app",
    "api": "voice_ai.api",
    "twilio": "voice_ai.integrations.twilio",
    "llm": "voice_ai.integrations.llm",
    "deepgram": "voice_ai.integrations.deepgram",
    "db": "voice_ai.db",
    "scheduler": "voice_ai.scheduler",
}


class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the log record.
    """
    def __init__(self, **kwargs):
        self.fmt_dict = kwargs

    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if available
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        
        # Add any custom fields
        for key, value in self.fmt_dict.items():
            if hasattr(record, key):
                log_record[key] = getattr(record, key)
            elif key in record.__dict__:
                log_record[key] = record.__dict__[key]
            else:
                log_record[key] = value
        
        # Add call trace info if available
        if hasattr(record, "trace_id"):
            log_record["trace_id"] = record.trace_id
        
        # Add user info if available
        if hasattr(record, "user_id"):
            log_record["user_id"] = record.user_id
        
        # Add call info if available
        if hasattr(record, "call_sid"):
            log_record["call_sid"] = record.call_sid

        return json.dumps(log_record)


def setup_logger(name, log_file=None, level=logging.INFO, formatter=None):
    """
    Set up a logger with the specified name and level
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear any existing handlers
    logger.handlers = []
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Set formatter
    if formatter is None:
        formatter = JSONFormatter()
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if specified
    if log_file:
        file_handler = RotatingFileHandler(
            logs_dir / log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(component="app"):
    """
    Get a logger for the specified component
    """
    logger_name = LOGGERS.get(component, LOGGERS["app"])
    
    # Determine log file based on component
    log_file = f"{component}.log"
    
    # Set log level based on environment
    log_level = getattr(logging, settings.LOG_LEVEL, logging.INFO)
    
    # Create formatter
    formatter = JSONFormatter(
        service="voice_ai",
        component=component,
        environment=settings.ENVIRONMENT
    )
    
    return setup_logger(logger_name, log_file, log_level, formatter)


def setup_middleware_logging():
    """
    Set up middleware for request logging
    """
    logger = get_logger("api")
    
    class LogMiddleware:
        async def __call__(self, request, call_next):
            # Generate trace ID
            import uuid
            trace_id = str(uuid.uuid4())
            
            # Log request
            logger.info(
                f"Request: {request.method} {request.url.path}",
                extra={
                    "trace_id": trace_id,
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": str(request.query_params),
                    "client_host": request.client.host if request.client else None,
                }
            )
            
            try:
                # Process request
                response = await call_next(request)
                
                # Log response
                logger.info(
                    f"Response: {response.status_code}",
                    extra={
                        "trace_id": trace_id,
                        "status_code": response.status_code,
                    }
                )
                
                return response
            except Exception as e:
                # Log exception
                logger.error(
                    f"Exception during request: {str(e)}",
                    exc_info=True,
                    extra={"trace_id": trace_id}
                )
                raise
    
    return LogMiddleware()


class RequestContextLogger:
    """
    Context manager for logging with request context
    """
    def __init__(self, component="app", **context):
        self.logger = get_logger(component)
        self.context = context
    
    def debug(self, msg, **kwargs):
        self.logger.debug(msg, extra={**self.context, **kwargs})
    
    def info(self, msg, **kwargs):
        self.logger.info(msg, extra={**self.context, **kwargs})
    
    def warning(self, msg, **kwargs):
        self.logger.warning(msg, extra={**self.context, **kwargs})
    
    def error(self, msg, exc_info=False, **kwargs):
        self.logger.error(msg, exc_info=exc_info, extra={**self.context, **kwargs})
    
    def critical(self, msg, exc_info=True, **kwargs):
        self.logger.critical(msg, exc_info=exc_info, extra={**self.context, **kwargs})


def get_call_logger(call_sid, user_id=None):
    """
    Get a logger with call context
    """
    return RequestContextLogger("twilio", call_sid=call_sid, user_id=user_id)


# Example integration with FastAPI
def configure_logging_middleware(app):
    """
    Configure logging middleware for FastAPI
    """
    from fastapi import Request, Response
    from starlette.middleware.base import BaseHTTPMiddleware
    import time
    import uuid
    
    logger = get_logger("api")
    
    class LoggingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            # Generate trace ID
            trace_id = str(uuid.uuid4())
            
            # Get start time
            start_time = time.time()
            
            # Get request details
            method = request.method
            path = request.url.path
            query_params = dict(request.query_params)
            client_host = request.client.host if request.client else None
            
            # Log request
            logger.info(
                f"Request: {method} {path}",
                extra={
                    "trace_id": trace_id,
                    "method": method,
                    "path": path,
                    "query_params": query_params,
                    "client_host": client_host,
                }
            )
            
            try:
                # Process request
                response = await call_next(request)
                
                # Calculate processing time
                process_time = time.time() - start_time
                
                # Log response
                logger.info(
                    f"Response: {response.status_code} (processed in {process_time:.4f} seconds)",
                    extra={
                        "trace_id": trace_id,
                        "status_code": response.status_code,
                        "process_time": process_time,
                    }
                )
                
                return response
            except Exception as e:
                # Calculate processing time
                process_time = time.time() - start_time
                
                # Log exception
                logger.error(
                    f"Exception during request: {str(e)} (processed in {process_time:.4f} seconds)",
                    exc_info=True,
                    extra={
                        "trace_id": trace_id,
                        "process_time": process_time,
                    }
                )
                raise
    
    app.add_middleware(LoggingMiddleware)


# Add to config.py
"""
# Add these to your settings class in config.py

LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
"""