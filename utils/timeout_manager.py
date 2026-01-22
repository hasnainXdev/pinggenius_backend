import asyncio
import signal
from functools import wraps
from typing import Callable, Any, Optional
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import logging


class TimeoutError(Exception):
    """Custom exception for timeout scenarios."""
    pass


def timeout_handler(signum, frame):
    """Handler for timeout signals."""
    raise TimeoutError("Operation timed out")


class TimeoutManager:
    """
    Manages timeout operations for various tasks, particularly for LLM processing.
    """
    
    def __init__(self, default_timeout: int = 8):
        """
        Initializes the timeout manager.
        
        Args:
            default_timeout: Default timeout in seconds (default 8 seconds as per requirements)
        """
        self.default_timeout = default_timeout
    
    async def run_with_timeout(self, coro, timeout: Optional[int] = None) -> Any:
        """
        Runs a coroutine with a specified timeout.
        
        Args:
            coro: The coroutine to run
            timeout: Timeout in seconds (uses default if not specified)
            
        Returns:
            Result of the coroutine
            
        Raises:
            TimeoutError: If the operation exceeds the timeout
        """
        timeout = timeout or self.default_timeout
        
        try:
            result = await asyncio.wait_for(coro, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            raise TimeoutError(f"Operation timed out after {timeout} seconds")
    
    def run_sync_with_timeout(self, func: Callable, timeout: Optional[int] = None, *args, **kwargs) -> Any:
        """
        Runs a synchronous function with a specified timeout using signal handling.
        
        Args:
            func: The function to run
            timeout: Timeout in seconds (uses default if not specified)
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            Result of the function
            
        Raises:
            TimeoutError: If the operation exceeds the timeout
        """
        timeout = timeout or self.default_timeout
        
        # Set up the signal handler for timeout
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            result = func(*args, **kwargs)
            signal.alarm(0)  # Cancel the alarm
            return result
        except TimeoutError:
            raise
        finally:
            signal.signal(signal.SIGALRM, old_handler)  # Restore old handler


# Decorator for applying timeout to functions
def with_timeout(seconds: Optional[int] = None):
    """
    Decorator to apply timeout to functions.
    
    Args:
        seconds: Number of seconds before timeout (uses default if not specified)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            timeout_manager = TimeoutManager()
            coro = func(*args, **kwargs)
            return await timeout_manager.run_with_timeout(coro, seconds)
        return wrapper
    return decorator


# Pre-configured timeout managers
llm_timeout_manager = TimeoutManager(default_timeout=8)  # 8 seconds for LLM processing
validation_timeout_manager = TimeoutManager(default_timeout=2)  # 2 seconds for validation