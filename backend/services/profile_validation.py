from typing import Optional, Dict, Any
from models.profile import LinkedInProfile
from models.validation import ValidationResult, FallbackMessage, PainPoint
from utils.validation import validate_linkedin_profile, generate_fallback_message
from utils.logging import log_validation_failure, log_fallback_message_returned
from utils.timeout_manager import llm_timeout_manager
import logging


class ProfileValidationService:
    """
    Service for validating LinkedIn profiles and preventing AI hallucination
    by ensuring sufficient context before processing.
    """

    def __init__(self):
        # Curated list of role/industry-specific pain points
        self.pain_point_mappings = {
            "software engineer": {
                "tech": "Scaling team productivity",
                "startup": "Technical debt management",
                "finance": "System reliability and uptime",
            },
            "product manager": {
                "tech": "Balancing feature velocity with quality",
                "healthcare": "Regulatory compliance in product development",
                "ecommerce": "Customer acquisition cost optimization",
            },
            "sales representative": {
                "saas": "Long sales cycles and deal velocity",
                "consulting": "Lead qualification efficiency",
                "retail": "Customer retention and loyalty",
            },
            "marketing manager": {
                "tech": "Measuring ROI on digital marketing channels",
                "agency": "Client retention and satisfaction",
                "ecommerce": "Conversion rate optimization",
            },
            "hr manager": {
                "tech": "Talent acquisition in competitive market",
                "healthcare": "Employee retention and burnout prevention",
                "finance": "Compliance with employment regulations",
            },
        }

    def validate_profile_completeness(
        self, profile: LinkedInProfile
    ) -> ValidationResult:
        """
        Validates that the profile contains the minimum required information
        (role, and either industry or company) to generate meaningful content.

        Args:
            profile: The LinkedIn profile to validate

        Returns:
            ValidationResult indicating whether the profile is valid
        """
        validation_result = validate_linkedin_profile(profile)

        if not validation_result.is_valid:
            # Log the validation failure for monitoring
            # Handle both object attributes and dictionary keys
            profile_url = getattr(profile, 'url', None) or (profile.get('url') if isinstance(profile, dict) else '')
            profile_role = getattr(profile, 'role', None) or (profile.get('role') if isinstance(profile, dict) else '')
            profile_company = getattr(profile, 'company', None) or (profile.get('company') if isinstance(profile, dict) else '')
            profile_industry = getattr(profile, 'industry', None) or (profile.get('industry') if isinstance(profile, dict) else '')

            profile_data = {
                "url": profile_url,
                "role": profile_role,
                "company": profile_company,
                "industry": profile_industry,
            }
            log_validation_failure(profile_data, validation_result.errors)

        return validation_result

    def check_role_requirement(self, profile: LinkedInProfile) -> bool:
        """
        Checks if the profile has a valid role field.

        Args:
            profile: The LinkedIn profile to check

        Returns:
            Boolean indicating if role requirement is met
        """
        # Handle both object attributes and dictionary keys
        profile_role = getattr(profile, 'role', None) or (profile.get('role') if isinstance(profile, dict) else '')
        return bool(profile_role and profile_role.strip())

    def check_company_or_industry_requirement(self, profile: LinkedInProfile) -> bool:
        """
        Checks if the profile has either a valid company or industry field.

        Args:
            profile: The LinkedIn profile to check

        Returns:
            Boolean indicating if company or industry requirement is met
        """
        # Handle both object attributes and dictionary keys
        profile_company = getattr(profile, 'company', None) or (profile.get('company') if isinstance(profile, dict) else '')
        profile_industry = getattr(profile, 'industry', None) or (profile.get('industry') if isinstance(profile, dict) else '')

        company_present = bool(profile_company and profile_company.strip())
        industry_present = bool(profile_industry and profile_industry.strip())

        return company_present or industry_present

    def generate_fallback_message(
        self, reason: str = "insufficient_context"
    ) -> FallbackMessage:
        """
        Creates a safe fallback message instead of attempting to generate outreach content.

        Args:
            reason: The reason for returning a fallback message

        Returns:
            FallbackMessage with appropriate content
        """
        fallback_msg = generate_fallback_message(reason)
        log_fallback_message_returned(
            reason, "unknown"
        )  # URL will be added when called from context
        return fallback_msg

    def enhance_error_message(
        self, validation_result: ValidationResult, profile: LinkedInProfile
    ) -> Dict[str, Any]:
        """
        Enhances error messages with actionable alternatives based on validation results.

        Args:
            validation_result: The validation result with errors
            profile: The LinkedIn profile that was validated

        Returns:
            Dictionary with enhanced error message and actionable alternatives
        """
        error_response = {
            "error": "Validation failed",
            "message": (
                "; ".join(validation_result.errors)
                if validation_result.errors
                else "Profile validation failed"
            ),
            "actionable_alternative": "Please provide a role, and either company or industry information for better results",
        }

        # Customize actionable alternatives based on specific validation failures
        if validation_result.errors:
            missing_fields = []

            # Handle both object attributes and dictionary keys
            profile_role = getattr(profile, 'role', None) or (profile.get('role') if isinstance(profile, dict) else '')
            profile_company = getattr(profile, 'company', None) or (profile.get('company') if isinstance(profile, dict) else '')
            profile_industry = getattr(profile, 'industry', None) or (profile.get('industry') if isinstance(profile, dict) else '')

            if not profile_role or not profile_role.strip():
                missing_fields.append("role")
            if not profile_company or not profile_company.strip():
                if not profile_industry or not profile_industry.strip():
                    missing_fields.extend(["company", "industry"])
            elif not profile_industry or not profile_industry.strip():
                if not profile_company or not profile_company.strip():
                    missing_fields.extend(["company", "industry"])

            if "role" in missing_fields:
                error_response["actionable_alternative"] = (
                    "Please provide the person's role or job title"
                )
            elif set(["company", "industry"]).issubset(set(missing_fields)):
                error_response["actionable_alternative"] = (
                    "Please provide either company or industry information"
                )
            elif "role" in missing_fields and set(["company", "industry"]).intersection(
                set(missing_fields)
            ):
                error_response["actionable_alternative"] = (
                    "Please provide the person's role and either company or industry information"
                )

        return error_response

    async def validate_and_process_profile(
        self, profile: LinkedInProfile
    ) -> Dict[str, Any]:
        """
        Performs complete validation of a profile and returns either validation results
        or a fallback message if validation fails.

        Args:
            profile: The LinkedIn profile to validate and process

        Returns:
            Dictionary containing either validation results or fallback message
        """
        # Validate profile completeness
        validation_result = self.validate_profile_completeness(profile)

        if not validation_result.is_valid:
            # Return fallback message to prevent AI hallucination
            fallback_msg = self.generate_fallback_message("insufficient_context")
            return {
                "fallback_message": fallback_msg.dict(),
                "validation_result": validation_result.dict(),
            }

        # If validation passes, return the validation result
        return {"validation_result": validation_result.dict(), "profile_ready": True}

    def infer_pain_point(self, profile: LinkedInProfile) -> Optional[PainPoint]:
        """
        Infers a specific pain point from the profile's role and industry
        using curated role/industry mappings.

        Args:
            profile: The LinkedIn profile to analyze

        Returns:
            PainPoint if one can be inferred, None otherwise
        """
        # Handle both object attributes and dictionary keys
        profile_role = getattr(profile, 'role', None) or (profile.get('role') if isinstance(profile, dict) else '')
        profile_industry = getattr(profile, 'industry', None) or (profile.get('industry') if isinstance(profile, dict) else '')

        if not profile_role or not profile_industry:
            return None

        role_lower = profile_role.lower()
        industry_lower = profile_industry.lower()

        # Look for role-specific pain points
        if role_lower in self.pain_point_mappings:
            role_mappings = self.pain_point_mappings[role_lower]

            # Look for industry-specific pain point
            if industry_lower in role_mappings:
                pain_point_desc = role_mappings[industry_lower]
                pain_point = PainPoint(
                    id=f"{role_lower}_{industry_lower}",
                    role=profile_role,
                    industry=profile_industry,
                    description=pain_point_desc,
                    category=self._get_category_for_pain_point(pain_point_desc),
                )

                from utils.logging import log_pain_point_inference

                log_pain_point_inference(
                    profile_role, profile_industry, pain_point.description
                )

                return pain_point
            else:
                # If no industry-specific mapping, use first available
                for industry, desc in role_mappings.items():
                    pain_point = PainPoint(
                        id=f"{role_lower}_{industry}",
                        role=profile_role,
                        industry=industry,
                        description=desc,
                        category=self._get_category_for_pain_point(desc),
                    )

                    from utils.logging import log_pain_point_inference

                    log_pain_point_inference(
                        profile_role, profile_industry, pain_point.description
                    )

                    return pain_point

        return None

    def _get_category_for_pain_point(self, pain_point_desc: str) -> str:
        """
        Determines the category for a pain point based on keywords in the description.

        Args:
            pain_point_desc: The pain point description

        Returns:
            Category string
        """
        desc_lower = pain_point_desc.lower()

        if any(
            keyword in desc_lower
            for keyword in ["sales", "revenue", "deal", "customer", "lead"]
        ):
            return "sales"
        elif any(
            keyword in desc_lower
            for keyword in ["marketing", "roi", "conversion", "channel", "campaign"]
        ):
            return "marketing"
        elif any(
            keyword in desc_lower
            for keyword in ["product", "feature", "quality", "development", "agile"]
        ):
            return "product"
        elif any(
            keyword in desc_lower
            for keyword in ["talent", "employee", "retention", "recruitment", "hr"]
        ):
            return "hr"
        elif any(
            keyword in desc_lower
            for keyword in ["technical", "system", "uptime", "debt", "scalability"]
        ):
            return "technology"
        else:
            return "general"
