from models.profile import LinkedInProfile
from typing import Optional
import logging
from utils.retry import retry_with_backoff
from config.settings import settings
from apify_client import ApifyClient
from utils.caching import cache


class ProfileService:
    def __init__(self):
        self.apify_client = (
            ApifyClient(settings.apify_api_key) if settings.apify_api_key else None
        )

    @retry_with_backoff(
        stop_attempts=3,
        wait_min=1,
        wait_max=10,
        retryable_exceptions=(Exception,),
    )
    async def analyze_profile(self, url: str) -> Optional[LinkedInProfile]:
        cache_key = f"profile:{url}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        profile = await self._analyze_profile_internal(url)
        cache.set(cache_key, profile, ttl=900)
        return profile

    async def _analyze_profile_internal(self, url: str) -> LinkedInProfile:
        try:
            if not url.startswith("https://www.linkedin.com/in/"):
                raise ValueError("Invalid LinkedIn profile URL")

            if not self.apify_client:
                logging.warning("Apify not configured, returning fallback profile")
                return self._fallback_profile(url)

            # ✅ Correct actor call
            run = self.apify_client.actor("dev_fusion/Linkedin-Profile-Scraper").call(
                run_input={
                    "profileUrls": [url],
                    "resultsLimit": 1,
                }
            )

            if run.get("status") != "SUCCEEDED":
                logging.error(f"Apify run failed: {run.get('status')}")
                return self._fallback_profile(url)

            dataset = self.apify_client.dataset(run["defaultDatasetId"])

            print("Apify dataset fetched:", dataset.list_items().items)

            items = []
            for item in dataset.iterate_items():
                items.append(item)
                break

            if not items:
                logging.warning("Apify returned empty dataset")
                return self._fallback_profile(url)

            data = items[0]

            return LinkedInProfile(
                url=url,
                role=data.get("jobTitle"),
                company=data.get("companyName"),
                industry=data.get("industry"),
                recent_activity=data.get("description"),
            )

        except Exception as e:
            logging.error(f"Error analyzing profile {url}: {e}")
            return self._fallback_profile(url)

    def _fallback_profile(self, url: str) -> LinkedInProfile:
        return LinkedInProfile(
            url=url,
            role="Unknown",
            company="Unknown",
            industry="Unknown",
            recent_activity=None,
        )

    def validate_profile_url(self, url: str) -> bool:
        return url.startswith("https://www.linkedin.com/in/")
