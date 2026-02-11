from fastapi import FastAPI, Request, HTTPException
from collections import defaultdict
import time
from typing import Dict
from config.settings import settings


class RateLimiter:
    def __init__(self, requests_per_minute: int = settings.requests_per_minute):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, identifier: str) -> bool:
        now = time.time()
        # Remove requests older than 1 minute
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier] if now - req_time < 60
        ]

        # Check if the client has exceeded the limit
        if len(self.requests[identifier]) >= self.requests_per_minute:
            return False

        # Add the current request
        self.requests[identifier].append(now)
        return True


def add_rate_limiting_middleware(app: FastAPI):
    """Add rate limiting middleware to the application"""
    rate_limiter = RateLimiter()

    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        # Use client IP as identifier (in production, consider using API keys)
        client_ip = request.client.host
        if not rate_limiter.is_allowed(client_ip):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        response = await call_next(request)
        return response
