"""
Validation utilities for document processing pipeline.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Expected fields for different document types
EXPECTED_FIELDS = {
    "license": {
        "Name": str,
        "DateOfBirth": str,
        "LicenseNumber": str,
        "IssuingState": str,
        "ExpiryDate": str
    },
    "receipt": {
        "MerchantName": str,
        "TotalAmount": str,
        "DateOfPurchase": str,
        "Items": list,
        "PaymentMethod": str
    }
}


def validate_license_output(data: Dict[str, Any]) -> bool:
    """
    Validate that license data has the correct structure.
    
    Args:
        data (Dict[str, Any]): Extracted license data
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        if not isinstance(data, dict):
            logger.error("License data is not a dictionary")
            return False
        
        expected_keys = set(EXPECTED_FIELDS["license"].keys())
        actual_keys = set(data.keys())
        
        # Check if all expected keys are present
        if not expected_keys.issubset(actual_keys):
            missing_keys = expected_keys - actual_keys
            logger.error(f"Missing required license keys: {missing_keys}")
            return False
        
        # Check data types
        for key, expected_type in EXPECTED_FIELDS["license"].items():
            if data[key] is not None and not isinstance(data[key], expected_type):
                logger.error(f"Invalid type for {key}: expected {expected_type}, got {type(data[key])}")
                return False
        
        logger.info("License output validation passed")
        return True
        
    except Exception as e:
        logger.error(f"License validation error: {e}")
        return False


def validate_receipt_output(data: Dict[str, Any]) -> bool:
    """
    Validate that receipt data has the correct structure.
    
    Args:
        data (Dict[str, Any]): Extracted receipt data
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        if not isinstance(data, dict):
            logger.error("Receipt data is not a dictionary")
            return False
        
        expected_keys = set(EXPECTED_FIELDS["receipt"].keys())
        actual_keys = set(data.keys())
        
        # Check if all expected keys are present
        if not expected_keys.issubset(actual_keys):
            missing_keys = expected_keys - actual_keys
            logger.error(f"Missing required receipt keys: {missing_keys}")
            return False
        
        # Check data types
        for key, expected_type in EXPECTED_FIELDS["receipt"].items():
            if data[key] is not None and not isinstance(data[key], expected_type):
                logger.error(f"Invalid type for {key}: expected {expected_type}, got {type(data[key])}")
                return False
        
        # Validate Items list structure
        if "Items" in data and data["Items"] is not None:
            if not isinstance(data["Items"], list):
                logger.error("Items field is not a list")
                return False
            
            # Validate each item in the list
            for i, item in enumerate(data["Items"]):
                if not isinstance(item, dict):
                    logger.error(f"Item {i} is not a dictionary")
                    return False
                
                required_item_keys = {"name", "quantity", "price"}
                if not required_item_keys.issubset(set(item.keys())):
                    missing_item_keys = required_item_keys - set(item.keys())
                    logger.error(f"Item {i} missing keys: {missing_item_keys}")
                    return False
        
        logger.info("Receipt output validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Receipt validation error: {e}")
        return False


def validate_extracted_data(data: Dict[str, Any], doc_type: str) -> bool:
    """
    Validate that extracted data has the correct structure.
    
    Args:
        data (Dict[str, Any]): Extracted data
        doc_type (str): Document type
        
    Returns:
        bool: True if valid, False otherwise
    """
    if doc_type == "license":
        return validate_license_output(data)
    elif doc_type == "receipt":
        return validate_receipt_output(data)
    else:
        logger.error(f"Unknown document type: {doc_type}")
        return False


def get_supported_document_types() -> List[str]:
    """Get list of supported document types."""
    return list(EXPECTED_FIELDS.keys())
