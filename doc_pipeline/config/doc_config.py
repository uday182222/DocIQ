"""
Document Configuration Module

This module registers supported document types with their configurations including:
- required_fields: list of keys the output must contain
- prompt_path: path to the LLM prompt
- validator_fn: function to validate the extracted output
- postprocess_fn: function to postprocess LLM output if needed
"""

from typing import Dict, List, Callable, Any, Optional
from pathlib import Path
import json


def validate_resume_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate resume extraction output.
    """
    required_fields = ["FullName"]
    optional_fields = ["Email", "PhoneNumber", "Skills", "WorkExperience", "Education"]
    
    # Check required fields
    for field in required_fields:
        if field not in data or data[field] is None:
            raise ValueError(f"Required field '{field}' is missing for resume")
    
    # Set defaults for optional fields
    validated_data = {}
    for field in required_fields:
        validated_data[field] = data[field]
    
    for field in optional_fields:
        if field in data and data[field] is not None:
            validated_data[field] = data[field]
        else:
            # Set defaults
            if field == "Skills":
                validated_data[field] = []
            elif field in ["WorkExperience", "Education"]:
                validated_data[field] = []
            else:
                validated_data[field] = None
    
    return validated_data


def validate_license_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate license extraction output.
    """
    required_fields = ["Name"]
    optional_fields = ["DateOfBirth", "LicenseNumber", "IssuingState", "ExpiryDate"]
    
    # Check required fields
    for field in required_fields:
        if field not in data or data[field] is None:
            raise ValueError(f"Required field '{field}' is missing for license")
    
    # Set defaults for optional fields
    validated_data = {}
    for field in required_fields:
        validated_data[field] = data[field]
    
    for field in optional_fields:
        if field in data and data[field] is not None:
            validated_data[field] = data[field]
        else:
            validated_data[field] = None
    
    return validated_data


def validate_receipt_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate receipt extraction output with discrepancy detection.
    """
    required_fields = ["StoreName", "TotalAmount", "LineItems"]
    optional_fields = ["StoreAddress", "StorePhone", "DateOfPurchase", "TransactionTime", 
                      "ReceiptID", "Subtotal", "Tax", "PaymentMethod", "CardLast4Digits", "DiscrepancyWarning"]
    
    # Check required fields
    for field in required_fields:
        if field not in data or data[field] is None:
            raise ValueError(f"Required field '{field}' is missing for receipt")
    
    # Validate LineItems structure
    if "LineItems" in data and isinstance(data["LineItems"], list):
        for i, item in enumerate(data["LineItems"]):
            if not isinstance(item, dict):
                raise ValueError(f"LineItem {i} is not a dictionary")
            if "name" not in item or not item["name"]:
                raise ValueError(f"LineItem {i} missing name")
            if "price" not in item or item["price"] is None:
                raise ValueError(f"LineItem {i} missing price")
    
    # Set defaults for optional fields
    validated_data = {}
    for field in required_fields:
        validated_data[field] = data[field]
    
    for field in optional_fields:
        if field in data and data[field] is not None:
            validated_data[field] = data[field]
        else:
            if field == "LineItems":
                validated_data[field] = []
            elif field == "DiscrepancyWarning":
                validated_data[field] = False
            else:
                validated_data[field] = None
    
    # Check for discrepancy warning
    if "LineItems" in validated_data and "TotalAmount" in validated_data:
        total_items_price = sum(float(item.get("price", 0)) for item in validated_data["LineItems"])
        total_amount = float(validated_data["TotalAmount"])
        
        if total_amount > 0:
            discrepancy_percentage = abs(total_items_price - total_amount) / total_amount
            if discrepancy_percentage > 0.02:  # 2% tolerance
                validated_data["DiscrepancyWarning"] = True
                print(f"Warning: Discrepancy detected. Sum of items: ${total_items_price:.2f}, Total: ${total_amount:.2f} ({discrepancy_percentage:.1%} difference)")
    
    return validated_data


def postprocess_resume_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Postprocess resume extraction output.
    """
    # Ensure skills are always a list
    if "Skills" in data and not isinstance(data["Skills"], list):
        if data["Skills"] is None:
            data["Skills"] = []
        else:
            data["Skills"] = [data["Skills"]]
    
    # Ensure work experience and education are always lists
    for field in ["WorkExperience", "Education"]:
        if field in data and not isinstance(data[field], list):
            if data[field] is None:
                data[field] = []
            else:
                data[field] = [data[field]]
    
    return data


def postprocess_license_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Postprocess license extraction output.
    """
    # No specific postprocessing needed for licenses
    return data


def postprocess_receipt_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Postprocess receipt extraction output.
    """
    # Ensure LineItems is always a list
    if "LineItems" in data and not isinstance(data["LineItems"], list):
        if data["LineItems"] is None:
            data["LineItems"] = []
        else:
            data["LineItems"] = [data["LineItems"]]
    
    # Ensure DiscrepancyWarning is boolean
    if "DiscrepancyWarning" in data:
        data["DiscrepancyWarning"] = bool(data["DiscrepancyWarning"])
    
    return data


# Document type configurations
DOCUMENT_CONFIGS = {
    "resume": {
        "required_fields": ["FullName"],
        "optional_fields": ["Email", "PhoneNumber", "Skills", "WorkExperience", "Education"],
        "prompt_path": "doc_pipeline/prompts/resume_extraction.txt",
        "validator_fn": validate_resume_output,
        "postprocess_fn": postprocess_resume_output
    },
    "license": {
        "required_fields": ["Name"],
        "optional_fields": ["DateOfBirth", "LicenseNumber", "IssuingState", "ExpiryDate"],
        "prompt_path": "doc_pipeline/prompts/license_extraction.txt",
        "validator_fn": validate_license_output,
        "postprocess_fn": postprocess_license_output
    },
    "receipt": {
        "required_fields": ["StoreName", "TotalAmount", "LineItems"],
        "optional_fields": ["StoreAddress", "StorePhone", "DateOfPurchase", "TransactionTime", 
                          "ReceiptID", "Subtotal", "Tax", "PaymentMethod", "CardLast4Digits", "DiscrepancyWarning"],
        "prompt_path": "doc_pipeline/prompts/receipt_extraction.txt",
        "validator_fn": validate_receipt_output,
        "postprocess_fn": postprocess_receipt_output
    }
}


def get_document_config(doc_type: str) -> Dict[str, Any]:
    """
    Get configuration for a specific document type.
    
    Args:
        doc_type: The document type (resume, license, receipt)
    
    Returns:
        Dictionary containing the document configuration
    
    Raises:
        ValueError: If document type is not supported
    """
    if doc_type not in DOCUMENT_CONFIGS:
        supported_types = list(DOCUMENT_CONFIGS.keys())
        raise ValueError(f"Unsupported document type: {doc_type}. Supported types: {supported_types}")
    
    return DOCUMENT_CONFIGS[doc_type]


def get_supported_document_types() -> List[str]:
    """
    Get list of supported document types.
    
    Returns:
        List of supported document type names
    """
    return list(DOCUMENT_CONFIGS.keys())


def validate_document_type(doc_type: str) -> bool:
    """
    Check if a document type is supported.
    
    Args:
        doc_type: The document type to check
    
    Returns:
        True if supported, False otherwise
    """
    return doc_type in DOCUMENT_CONFIGS


def get_prompt_path(doc_type: str) -> Path:
    """
    Get the prompt file path for a document type.
    
    Args:
        doc_type: The document type
    
    Returns:
        Path to the prompt file
    
    Raises:
        ValueError: If document type is not supported
    """
    config = get_document_config(doc_type)
    return Path(config["prompt_path"])


def get_validator_function(doc_type: str) -> Callable:
    """
    Get the validation function for a document type.
    
    Args:
        doc_type: The document type
    
    Returns:
        Validation function
    
    Raises:
        ValueError: If document type is not supported
    """
    config = get_document_config(doc_type)
    return config["validator_fn"]


def get_postprocess_function(doc_type: str) -> Callable:
    """
    Get the postprocessing function for a document type.
    
    Args:
        doc_type: The document type
    
    Returns:
        Postprocessing function
    
    Raises:
        ValueError: If document type is not supported
    """
    config = get_document_config(doc_type)
    return config["postprocess_fn"] 