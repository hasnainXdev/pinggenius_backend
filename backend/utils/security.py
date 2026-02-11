"""
Security hardening measures for the PingGenius application
"""
from fastapi import FastAPI
from fastapi.security import HTTPBearer
import re


def add_security_headers(app: FastAPI):
    """
    Add security headers to the application
    """

    @app.middleware("http")
    async def add_security_headers_middleware(request, call_next):
        response = await call_next(request)
        # Add security headers to all responses
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers[
            "Strict-Transport-Security"
        ] = "max-age=31536000; includeSubDomains"
        return response


def validate_input(input_str: str, pattern: str = None) -> bool:
    """
    Validate input strings to prevent injection attacks
    """
    if not input_str or not isinstance(input_str, str):
        return False

    # Check for potentially dangerous patterns
    dangerous_patterns = [
        r"<script",  # XSS attempts
        r"javascript:",  # XSS attempts
        r"on\w+\s*=",  # Event handlers
        r"<iframe",  # Frame injection
        r"<object",  # Object injection
        r"<embed",  # Embed injection
    ]

    input_lower = input_str.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, input_lower):
            return False

    # If a specific pattern is provided, validate against it
    if pattern:
        if not re.match(pattern, input_str):
            return False

    return True


def sanitize_input(input_str: str) -> str:
    """
    Sanitize input strings to remove potentially dangerous content
    """
    if not input_str or not isinstance(input_str, str):
        return ""

    # Remove potentially dangerous patterns
    sanitized = input_str
    dangerous_patterns = [
        r"<script[^>]*>.*?</script>",  # Script tags
        r"javascript:",  # JavaScript protocol
        r"on\w+\s*=",  # Event handlers
        r"<iframe[^>]*>.*?</iframe>",  # Iframe tags
        r"<object[^>]*>.*?</object>",  # Object tags
        r"<embed[^>]*>.*?</embed>",  # Embed tags
    ]

    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)

    return sanitized.strip()


def validate_linkedin_url(url: str) -> bool:
    """
    Validate that the URL is a proper LinkedIn profile URL
    """
    if not url or not isinstance(url, str):
        return False

    # LinkedIn profile URL pattern
    linkedin_pattern = r"^https?://(www\.)?linkedin\.com/in/[\w-]+/?$"

    return bool(re.match(linkedin_pattern, url))


def validate_profile_data(profile_data: dict) -> bool:
    """
    Validate profile data to ensure it doesn't contain malicious content
    """
    required_fields = ["url", "role", "company", "industry"]

    for field in required_fields:
        if field not in profile_data:
            return False

        value = profile_data[field]
        if not value or not isinstance(value, str):
            return False

        # Validate URL specifically
        if field == "url":
            if not validate_linkedin_url(value):
                return False
        else:
            # For other fields, ensure they don't contain malicious content
            if not validate_input(value):
                return False

    return True
