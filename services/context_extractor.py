from models.profile import LinkedInProfile
from models.validation import PainPoint
from typing import Dict, Any, List, Optional
import logging


class ContextExtractor:
    """
    Extracts relevant context from LinkedIn profile data for message generation
    """

    def __init__(self):
        # Curated list of role/industry-specific pain points
        self.pain_point_mappings = {
            "software engineer": [
                PainPoint(
                    id="pe1",
                    role="software engineer",
                    category="productivity",
                    description="Scaling team productivity"
                ),
                PainPoint(
                    id="pe2",
                    role="software engineer",
                    category="hiring",
                    description="Finding qualified candidates"
                )
            ],
            "sales manager": [
                PainPoint(
                    id="ps1",
                    role="sales manager",
                    category="lead_generation",
                    description="Generating qualified leads"
                ),
                PainPoint(
                    id="ps2",
                    role="sales manager",
                    category="conversion",
                    description="Improving conversion rates"
                )
            ],
            "marketing director": [
                PainPoint(
                    id="pm1",
                    role="marketing director",
                    category="roi",
                    description="Measuring marketing ROI"
                ),
                PainPoint(
                    id="pm2",
                    role="marketing director",
                    category="brand_awareness",
                    description="Increasing brand awareness"
                )
            ],
            "product manager": [
                PainPoint(
                    id="pp1",
                    role="product manager",
                    category="user_research",
                    description="Understanding user needs"
                ),
                PainPoint(
                    id="pp2",
                    role="product manager",
                    category="prioritization",
                    description="Prioritizing feature requests"
                )
            ],
            "cto": [
                PainPoint(
                    id="pc1",
                    role="cto",
                    category="security",
                    description="Securing company infrastructure"
                ),
                PainPoint(
                    id="pc2",
                    role="cto",
                    category="scaling",
                    description="Scaling technical infrastructure"
                )
            ],
            "founder": [
                PainPoint(
                    id="pf1",
                    role="founder",
                    category="funding",
                    description="Securing funding for growth"
                ),
                PainPoint(
                    id="pf2",
                    role="founder",
                    category="team_building",
                    description="Building a strong team"
                )
            ]
        }

    def extract_context(self, profile: LinkedInProfile) -> Dict[str, Any]:
        """
        Extract context from a LinkedIn profile for message generation
        """
        try:
            # Handle both object attributes and dictionary keys
            profile_url = getattr(profile, 'url', None) or (profile.get('url') if isinstance(profile, dict) else '')
            profile_role = getattr(profile, 'role', None) or (profile.get('role') if isinstance(profile, dict) else '')
            profile_company = getattr(profile, 'company', None) or (profile.get('company') if isinstance(profile, dict) else '')
            profile_industry = getattr(profile, 'industry', None) or (profile.get('industry') if isinstance(profile, dict) else '')
            profile_recent_activity = getattr(profile, 'recent_activity', None) or (profile.get('recent_activity') if isinstance(profile, dict) else '')

            context = {
                "profile_url": profile_url,
                "role": profile_role,
                "company": profile_company,
                "industry": profile_industry,
                "recent_activity": profile_recent_activity,
                "person_name": self._extract_name_from_url(profile_url),
                "pain_point": self._infer_pain_point(profile)
            }

            return context
        except Exception as e:
            logging.error(f"Error extracting context from profile {profile.id}: {e}")
            raise

    def _infer_pain_point(self, profile: LinkedInProfile) -> Optional[str]:
        """
        Infers a specific pain point from the profile's role and industry to improve outreach effectiveness.

        Args:
            profile: LinkedInProfile object to analyze

        Returns:
            String description of the pain point if found, None otherwise
        """
        # Handle both object attributes and dictionary keys
        profile_role = getattr(profile, 'role', None) or (profile.get('role') if isinstance(profile, dict) else '')

        if not profile_role:
            return None

        role_lower = profile_role.lower()

        # Look for exact role matches first
        if role_lower in self.pain_point_mappings:
            pain_points = self.pain_point_mappings[role_lower]

            # Handle both object attributes and dictionary keys for industry
            profile_industry = getattr(profile, 'industry', None) or (profile.get('industry') if isinstance(profile, dict) else '')

            # If industry is specified, try to find industry-specific pain points
            if profile_industry:
                industry_specific = [pp for pp in pain_points if pp.industry and pp.industry.lower() == profile_industry.lower()]
                if industry_specific:
                    return industry_specific[0].description  # Take the first match

            # If no industry-specific match, return the first general pain point
            if pain_points:
                return pain_points[0].description

        # If no exact match, try partial matching
        for role_key, pain_points in self.pain_point_mappings.items():
            if role_lower in role_key or role_key in role_lower:
                pain_point = pain_points[0]  # Take the first match
                return pain_point.description

        return None

    def _extract_name_from_url(self, url: str) -> str:
        """
        Extract the person's name from the LinkedIn profile URL
        """
        try:
            # LinkedIn URLs are in the format: https://www.linkedin.com/in/{name}
            name_part = url.rstrip("/").split("/")[-1]
            # Replace hyphens with spaces and title case
            name = name_part.replace("-", " ").title()
            return name
        except Exception:
            # If URL parsing fails, return a generic name
            return "LinkedIn User"

    def validate_context(self, context: Dict[str, Any]) -> bool:
        """
        Validate that the extracted context has the required fields for message generation
        """
        required_fields = ["role", "company", "industry"]
        for field in required_fields:
            if not context.get(field) or context[field] == "Unknown":
                return False
        return True
