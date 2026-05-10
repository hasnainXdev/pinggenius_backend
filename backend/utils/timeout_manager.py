import asyncio
from typing import Any, Optional
import logging


class TimeoutError(Exception):
    pass


class TimeoutManager:
    def __init__(self, default_timeout: int = 8):
        self.default_timeout = default_timeout

    async def run_with_timeout(self, coro, timeout: Optional[int] = None) -> Any:
        timeout = timeout or self.default_timeout
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Operation timed out after {timeout} seconds")


llm_timeout_manager = TimeoutManager(default_timeout=8)
validation_timeout_manager = TimeoutManager(default_timeout=2)
