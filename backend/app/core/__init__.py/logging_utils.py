import functools
import time
import inspect
from contextvars import ContextVar
from app.core.logging import get_logger, RequestContextLogger

# Create context variables for request context
current_trace_id = ContextVar('current_trace_id', default=None)
current_user_id = ContextVar('current_user_id', default=None)
current_call_sid = ContextVar('current_call_sid', default=None)

def set_context(trace_id=None, user_id=None, call_sid=None):
    """
    Set the current request context
    """
    if trace_id:
        current_trace_id.set(trace_id)
    if user_id:
        current_user_id.set(user_id)
    if call_sid:
        current_call_sid.set(call_sid)

def get_context():
    """
    Get the current request context
    """
    return {
        'trace_id': current_trace_id.get(),
        'user_id': current_user_id.get(),
        'call_sid': current_call_sid.get()
    }

def log_execution_time(component="app"):
    """
    Decorator to log the execution time of a function
    
    Usage:
        @log_execution_time("llm")
        async def generate_response(self, prompt):
            ...
    """
    logger = get_logger(component)
    
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get function details
            func_name = func.__name__
            module_name = func.__module__
            
            # Get context
            context = get_context()
            
            # Start timer
            start_time = time.time()
            
            # Log function call
            logger.debug(
                f"Starting {module_name}.{func_name}",
                extra={
                    **context,
                    'function': func_name,
                    'module': module_name,
                }
            )
            
            try:
                # Call the function
                result = await func(*args, **kwargs)
                
                # Calculate execution time
                execution_time = time.time() - start_time
                
                # Log success
                logger.debug(
                    f"Completed {module_name}.{func_name} in {execution_time:.4f} seconds",
                    extra={
                        **context,
                        'function': func_name,
                        'module': module_name,
                        'execution_time': execution_time,
                        'status': 'success'
                    }
                )
                
                return result
            except Exception as e:
                # Calculate execution time
                execution_time = time.time() - start_time
                
                # Log error
                logger.error(
                    f"Error in {module_name}.{func_name}: {str(e)}",
                    exc_info=True,
                    extra={
                        **context,
                        'function': func_name,
                        'module': module_name,
                        'execution_time': execution_time,
                        'status': 'error'
                    }
                )
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Get function details
            func_name = func.__name__
            module_name = func.__module__
            
            # Get context
            context = get_context()
            
            # Start timer
            start_time = time.time()
            
            # Log function call
            logger.debug(
                f"Starting {module_name}.{func_name}",
                extra={
                    **context,
                    'function': func_name,
                    'module': module_name,
                }
            )
            
            try:
                # Call the function
                result = func(*args, **kwargs)
                
                # Calculate execution time
                execution_time = time.time() - start_time
                
                # Log success
                logger.debug(
                    f"Completed {module_name}.{func_name} in {execution_time:.4f} seconds",
                    extra={
                        **context,
                        'function': func_name,
                        'module': module_name,
                        'execution_time': execution_time,
                        'status': 'success'
                    }
                )
                
                return result
            except Exception as e:
                # Calculate execution time
                execution_time = time.time() - start_time
                
                # Log error
                logger.error(
                    f"Error in {module_name}.{func_name}: {str(e)}",
                    exc_info=True,
                    extra={
                        **context,
                        'function': func_name,
                        'module': module_name,
                        'execution_time': execution_time,
                        'status': 'error'
                    }
                )
                raise
        
        # Check if the function is async
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
