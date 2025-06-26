"""
Irish Driving License Parser

This module contains parsers for extracting structured data from Irish driving license OCR text.
"""

import re
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def parse_irish_driving_license(text: str) -> Dict[str, Optional[str]]:
    """
    Parse Irish driving license text using regex patterns.
    
    Args:
        text (str): OCR extracted text from Irish driving license
        
    Returns:
        Dict[str, Optional[str]]: Extracted fields with None for failed matches
    """
    logger.info("Parsing Irish driving license text")
    
    # Initialize result dictionary
    result = {
        "Name": None,
        "DateOfBirth": None,
        "LicenseNumber": None,
        "IssuingState": None,
        "ExpiryDate": None
    }
    
    try:
        # Extract Name from fields 1. and 2. (Surname + First name)
        # Handle variations: "1. Collins 2. Aaron" or "1, Collins 2 Aaron"
        name_pattern = r'1[.,]\s*([A-Za-z\s]+?)\s*2[.,]?\s*([A-Za-z\s]+?)(?:\s|$)'
        name_match = re.search(name_pattern, text)
        if name_match:
            surname = name_match.group(1).strip()
            first_name = name_match.group(2).strip()
            result["Name"] = f"{first_name} {surname}".strip()
            logger.debug(f"Extracted name: {result['Name']}")
        
        # Extract Date of Birth from field 3.
        # Handle variations: "3. 09.10.56" or "3. 09.10.56"
        dob_pattern = r'3[.,]\s*(\d{2}\.\d{2}\.\d{2})'
        dob_match = re.search(dob_pattern, text)
        if dob_match:
            result["DateOfBirth"] = dob_match.group(1)
            logger.debug(f"Extracted date of birth: {result['DateOfBirth']}")
        
        # Extract License Number from field 5. (driver number)
        # Also try to find it after "RTSD" or similar patterns
        license_pattern = r'5[.,]\s*([A-Z0-9]+)'
        license_match = re.search(license_pattern, text)
        if license_match:
            result["LicenseNumber"] = license_match.group(1)
            logger.debug(f"Extracted license number: {result['LicenseNumber']}")
        else:
            # Try alternative pattern: look for alphanumeric string after RTSD
            alt_license_pattern = r'RTSD\s*([A-Z0-9]+)'
            alt_match = re.search(alt_license_pattern, text)
            if alt_match:
                result["LicenseNumber"] = alt_match.group(1)
                logger.debug(f"Extracted license number (alt): {result['LicenseNumber']}")
        
        # Extract Issuing State - hardcode as "Ireland" if IRL is present
        if 'IRL' in text:
            result["IssuingState"] = "Ireland"
            logger.debug("Detected Ireland as issuing state")
        
        # Extract Expiry Date from field 4b.
        # Handle variations: "4b. 14.04.67" or "4b, 14.04.67"
        expiry_pattern = r'4b[.,]\s*(\d{2}\.\d{2}\.\d{2})'
        expiry_match = re.search(expiry_pattern, text)
        if expiry_match:
            result["ExpiryDate"] = expiry_match.group(1)
            logger.debug(f"Extracted expiry date: {result['ExpiryDate']}")
        
        # Log extraction summary
        extracted_fields = [field for field, value in result.items() if value is not None]
        logger.info(f"Successfully extracted {len(extracted_fields)} fields: {extracted_fields}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error parsing Irish driving license: {e}")
        return result


def validate_irish_license_fields(fields: Dict[str, Optional[str]]) -> bool:
    """
    Validate extracted Irish driving license fields.
    
    Args:
        fields (Dict[str, Optional[str]]): Extracted fields
        
    Returns:
        bool: True if fields are valid, False otherwise
    """
    required_fields = ["Name", "DateOfBirth", "LicenseNumber", "IssuingState", "ExpiryDate"]
    
    # Check if all required fields are present (even if None)
    for field in required_fields:
        if field not in fields:
            logger.warning(f"Missing required field: {field}")
            return False
    
    # Check if at least some fields were extracted
    extracted_count = sum(1 for value in fields.values() if value is not None)
    if extracted_count == 0:
        logger.warning("No fields were successfully extracted")
        return False
    
    logger.info(f"Validation passed: {extracted_count}/{len(required_fields)} fields extracted")
    return True


def get_irish_license_parser_info() -> Dict[str, str]:
    """
    Get information about the Irish driving license parser.
    
    Returns:
        Dict[str, str]: Parser information
    """
    return {
        "name": "Irish Driving License Parser",
        "version": "1.0.0",
        "description": "Extracts structured data from Irish driving license OCR text using regex patterns",
        "supported_fields": ["Name", "DateOfBirth", "LicenseNumber", "IssuingState", "ExpiryDate"],
        "field_patterns": {
            "Name": "Fields 1. (Surname) + 2. (First name)",
            "DateOfBirth": "Field 3. (DD.MM.YY format)",
            "LicenseNumber": "Field 5. (Driver number)",
            "IssuingState": "Hardcoded as 'Ireland' if IRL present",
            "ExpiryDate": "Field 4b. (DD.MM.YY format)"
        }
    } 