from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from typing import Callable, TypeVar, Any
import logging

T = TypeVar("T")


def retry_with_backoff(
    stop_attempts: int = 3,
    wait_min: int = 1,
    wait_max: int = 10,
    retryable_exceptions: tuple = (Exception,),
) -> Callable:
    """
    Decorator to add retry logic with exponential backoff to a function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @retry(
            stop=stop_after_attempt(stop_attempts),
            wait=wait_exponential(multiplier=1, min=wait_min, max=wait_max),
            retry=retry_if_exception_type(retryable_exceptions),
            reraise=True,
        )
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                result = func(*args, **kwargs)
                return result
            except retryable_exceptions as e:
                logging.warning(f"Attempt failed for {func.__name__}: {e}. Retrying...")
                raise

        return wrapper

    return decorator


# Example usage:
# @retry_with_backoff(stop_attempts=3, wait_min=1, wait_max=10)
# def example_api_call():
#     # Your API call code here
#     pass
