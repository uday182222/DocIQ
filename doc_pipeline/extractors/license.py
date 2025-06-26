"""
Driving License Extractor Module
"""

import json
import logging
import sys
from typing import Dict, Any, Optional
from pathlib import Path

# Add the project root to the path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import the Gemini client function
try:
    from llm.gemini_client import extract_fields_from_text
except ImportError:
    # Fallback for when gemini_client is not yet implemented
    def extract_fields_from_text(text: str, doc_type: str) -> Dict[str, Any]:
        """Placeholder function until gemini_client is implemented."""
        raise NotImplementedError("extract_fields_from_text not yet implemented")

# Import validation function
try:
    from utils.validators import validate_license_output
except ImportError:
    # Fallback for when validators is not yet implemented
    def validate_license_output(data: Dict[str, Any]) -> bool:
        """Placeholder function until validators is implemented."""
        raise NotImplementedError("validate_license_output not yet implemented")

logger = logging.getLogger(__name__)

# Expected fields for driving license
EXPECTED_FIELDS = {
    "Name": str,
    "DateOfBirth": str, 
    "LicenseNumber": str,
    "IssuingState": str,
    "ExpiryDate": str
}


def parse_license(text: str) -> Dict[str, Any]:
    """
    Parse driving license text and extract structured data.
    
    Args:
        text (str): OCR extracted text from driving license
        
    Returns:
        Dict[str, Any]: JSON-ready dictionary with extracted fields
        
    Raises:
        ValueError: If validation fails
        Exception: If extraction fails
    """
    logger.info("Parsing driving license text")
    
    # Call Gemini client to extract fields
    try:
        extracted_data = extract_fields_from_text(text, doc_type="license")
        logger.info("Successfully extracted fields from text")
    except Exception as e:
        logger.error(f"Failed to extract fields: {e}")
        raise Exception(f"Field extraction failed: {e}")
    
    # Validate the extracted data using validate_license_output
    if not validate_license_output(extracted_data):
        logger.error("License output validation failed")
        raise ValueError("Extracted data failed validation - invalid structure or data types")
    
    logger.info("License parsing completed successfully")
    return extracted_data


def _validate_license_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that all expected fields are present and have correct types.
    
    Args:
        data (Dict[str, Any]): Raw extracted data
        
    Returns:
        Dict[str, Any]: Validated data
        
    Raises:
        ValueError: If validation fails
    """
    if not isinstance(data, dict):
        raise ValueError("Extracted data must be a dictionary")
    
    validated_data = {}
    
    for field_name, expected_type in EXPECTED_FIELDS.items():
        if field_name not in data:
            logger.warning(f"Missing field: {field_name}")
            validated_data[field_name] = None
            continue
            
        field_value = data[field_name]
        
        # Check if value is null/None
        if field_value is None:
            validated_data[field_name] = None
            continue
            
        # Check if value is string (including empty string)
        if isinstance(field_value, str):
            # Convert empty strings to None for consistency
            validated_data[field_name] = field_value.strip() if field_value.strip() else None
        else:
            logger.warning(f"Field {field_name} has unexpected type: {type(field_value)}")
            validated_data[field_name] = None
    
    logger.info("Field validation completed")
    return validated_data


def get_expected_fields() -> Dict[str, type]:
    """Get the expected fields and their types for driving license."""
    return EXPECTED_FIELDS.copy()
