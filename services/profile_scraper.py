from models.profile import LinkedInProfile
from typing import Optional
import logging
from utils.retry import retry_with_backoff
from config.settings import settings
import requests
from apify_client import ApifyClient
from utils.caching import cache


class ProfileService:
    def __init__(self):
        self.apify_client = (
            ApifyClient(settings.apify_api_key) if settings.apify_api_key else None
        )

    @retry_with_backoff(
        stop_attempts=3, wait_min=1, wait_max=10, retryable_exceptions=(Exception,)
    )
    async def analyze_profile(self, url: str) -> Optional[LinkedInProfile]:
        # Apply caching manually to avoid decorator conflicts
        cache_key = f"profile:{url}"
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        result = await self._analyze_profile_internal(url)
        cache.set(cache_key, result, ttl=900)  # Cache for 15 minutes
        return result

    async def _analyze_profile_internal(self, url: str) -> Optional[LinkedInProfile]:
        """
        Analyze a LinkedIn profile and extract context for message generation
        """
        try:
            # Validate URL format
            if not url.startswith("https://www.linkedin.com/in/"):
                raise ValueError("Invalid LinkedIn profile URL")

            # Use Apify to scrape the profile
            if self.apify_client:
                # Run the LinkedIn profile scraper actor
                run = self.apify_client.actor("apify/linkedin-profile-scraper").call(
                    run_input={"startUrls": [url]}
                )

                # Fetch the results
                dataset = self.apify_client.dataset(run["defaultDatasetId"]).get_items()
                profile_data = dataset["items"][0] if dataset["items"] else None

                if profile_data:
                    # Extract relevant information
                    profile = LinkedInProfile(
                        url=url,
                        role=profile_data.get("jobTitle", "Unknown"),
                        company=profile_data.get("companyName", "Unknown"),
                        industry=profile_data.get("industry", "Unknown"),
                        recent_activity=profile_data.get("description", None),
                    )
                    return profile
                else:
                    # Return a profile with minimal data if scraping failed
                    return LinkedInProfile(
                        url=url,
                        role="Unknown",
                        company="Unknown",
                        industry="Unknown",
                        recent_activity=None,
                    )
            else:
                # Fallback: mock data for development
                logging.warning("Apify client not configured, using mock data")
                profile = LinkedInProfile(
                    url=url,
                    role="Software Engineer",
                    company="Tech Corp",
                    industry="Technology",
                    recent_activity="Published article on software development",
                )
                return profile

        except Exception as e:
            logging.error(f"Error analyzing profile {url}: {e}")
            # Return a profile with minimal data instead of raising the exception
            # The calling function will handle the validation
            return LinkedInProfile(
                url=url,
                role="Unknown",
                company="Unknown",
                industry="Unknown",
                recent_activity=None,
            )

    def validate_profile_url(self, url: str) -> bool:
        """
        Validate if the provided URL is a valid LinkedIn profile URL
        """
        return url.startswith("https://www.linkedin.com/in/")
