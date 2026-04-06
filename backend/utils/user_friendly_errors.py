"""
Module for handling user-friendly error messages.
This module provides functions to convert technical error messages into simple, 
fun, and easy-to-understand messages that even a 10-year-old could understand.
"""

import re
from typing import Dict, Tuple


def get_user_friendly_error(error_message: str, original_error: str = "") -> Tuple[str, str]:
    """
    Converts a technical error message into a user-friendly message.
    
    Args:
        error_message: The error message to convert
        original_error: The original technical error (optional)
    
    Returns:
        A tuple containing (friendly_message, actionable_tip)
    """
    
    # Define patterns and corresponding friendly messages
    error_patterns: Dict[str, Tuple[str, str]] = {
        r"duplicate key error.*url_1": (
            "Oops! 📋 We've already seen this LinkedIn profile before!",
            "No worries though - we can only analyze each profile once. Try a different profile or check your dashboard for the existing analysis."
        ),
        r"E11000 duplicate key error": (
            "Hold up! 🛑 This profile is already in our system!",
            "We've already analyzed this person's LinkedIn. Why not try someone else or find the existing analysis in your dashboard?"
        ),
        r"connection.*refused|timeout": (
            "Uh oh! 🔌 We're having trouble connecting to our servers!",
            "This usually means there's a temporary hiccup. Just wait a moment and try again!"
        ),
        r"validation.*failed|invalid.*url": (
            "Hmm... 🤔 That doesn't look like a valid LinkedIn URL!",
            "Make sure you're copying the full LinkedIn profile URL starting with https://www.linkedin.com/in/"
        ),
        r"network.*error": (
            "Connection trouble! 🌐 Something's blocking our signal!",
            "Check your internet connection and try again. Sometimes it just takes a retry!"
        ),
        r"not found|404": (
            "Profile not found! 👤 The LinkedIn profile you entered doesn't exist!",
            "Double-check the URL you entered. Make sure the person really exists on LinkedIn!"
        ),
        r"rate limit|too many requests": (
            "Woah there, speedy! ⚡ You're going faster than we can handle!",
            "Slow down a bit and wait a few seconds before trying again. We appreciate your enthusiasm!"
        ),
        r"timeout|timed out": (
            "Taking too long! ⏳ Our system got tired waiting!",
            "Sometimes this happens with complex profiles. Try again, and maybe grab a snack while you wait!"
        ),
        r"internal.*error|500": (
            "Oops! Our robot made a mistake! 🤖", 
            "Don't worry, this happens sometimes. Try again in a bit, and our robots will hopefully behave better!"
        )
    }
    
    # Convert to lowercase for matching
    lower_error = error_message.lower()
    
    # Check for matches
    for pattern, (friendly_msg, tip) in error_patterns.items():
        if re.search(pattern, lower_error):
            return friendly_msg, tip
    
    # If no specific pattern matched, return a generic friendly message
    return (
        "Oops! Something unexpected happened! 🙈",
        "Don't worry, these things happen. Try again, and if it keeps happening, let us know!"
    )


def format_error_for_frontend(error_obj: Exception) -> Dict[str, str]:
    """
    Formats an error object for the frontend with user-friendly messages.
    
    Args:
        error_obj: The exception object
        
    Returns:
        A dictionary with user-friendly error information
    """
    error_str = str(error_obj)
    
    # Get user-friendly message
    friendly_msg, actionable_tip = get_user_friendly_error(error_str, str(error_obj))
    
    return {
        "user_friendly_message": friendly_msg,
        "actionable_tip": actionable_tip,
        "technical_details": error_str  # Still provide technical details for debugging
    }