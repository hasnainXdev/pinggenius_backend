from models.profile import LinkedInProfile
from typing import Optional
import logging
from utils.caching import cache


class ProfileService:
    def __init__(self):
        # No external scraper dependencies needed
        pass

    async def analyze_profile(self, profile_data: dict) -> Optional[LinkedInProfile]:
        """
        Analyze profile data that has been provided directly by the user
        """
        cache_key = f"profile:{profile_data.get('url', '')}:{hash(str(sorted(profile_data.items())))}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        profile = self._create_profile_from_data(profile_data)
        cache.set(cache_key, profile, ttl=900)
        return profile

    def _create_profile_from_data(self, profile_data: dict) -> LinkedInProfile:
        """
        Create a LinkedInProfile object from provided data
        """
        try:
            # Validate URL format
            url = profile_data.get('url', '')
            if not url.startswith("https://www.linkedin.com/in/"):
                raise ValueError("Invalid LinkedIn profile URL")

            # Create profile with provided data
            profile = LinkedInProfile(
                url=url,
                role=profile_data.get('role', ''),
                company=profile_data.get('company', ''),
                industry=profile_data.get('industry', ''),
                recent_activity=profile_data.get('recent_activity'),
                tone=profile_data.get('tone', 'FRIENDLY')
            )

            return profile

        except Exception as e:
            logging.error(f"Error creating profile from data: {e}")
            raise

    def validate_profile_url(self, url: str) -> bool:
        return url.startswith("https://www.linkedin.com/in/")
