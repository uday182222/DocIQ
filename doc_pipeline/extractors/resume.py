import logging
import re
from pathlib import Path
from parsers.resume_parser import fast_regex_resume_parse, RESUME_FIELDS
from llm.gemini_client import call_gemini_resume_extraction

logger = logging.getLogger(__name__)

def is_valid_phone_number(phone: str) -> bool:
    """Check if a phone number is valid (not a date range)."""
    if not phone:
        return False
    # Check if it looks like a date range (contains dash and digits)
    if re.search(r'\d+-\d+', phone):
        return False
    # Check if it has at least 10 digits
    digits = re.findall(r'\d', phone)
    return len(digits) >= 10

def parse_resume(text: str) -> dict:
    """
    Extract resume fields using fast regex, fallback to Gemini if needed.
    """
    result = fast_regex_resume_parse(text)
    
    # Check for missing/unclear fields or invalid data
    missing_or_invalid = []
    for f in RESUME_FIELDS:
        value = result.get(f)
        if not value or (isinstance(value, list) and not value):
            missing_or_invalid.append(f)
        elif f == "PhoneNumber" and not is_valid_phone_number(value):
            missing_or_invalid.append(f)
    
    if missing_or_invalid:
        logger.info(f"Falling back to Gemini for fields: {missing_or_invalid}")
        gemini_result = call_gemini_resume_extraction(text)
        # Merge: prefer regex result if valid, else Gemini
        for f in RESUME_FIELDS:
            value = result.get(f)
            if (not value or (isinstance(value, list) and not value) or 
                (f == "PhoneNumber" and not is_valid_phone_number(value))):
                result[f] = gemini_result.get(f)
    
    return result 