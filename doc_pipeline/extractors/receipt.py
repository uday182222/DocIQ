"""
Receipt extractor for processing shop receipts.
"""

import logging
from typing import Dict, Any, List
from llm.gemini_client import extract_fields_from_text
from utils.validators import validate_receipt_output

logger = logging.getLogger(__name__)


def parse_receipt(text: str) -> Dict[str, Any]:
    """
    Parse receipt text and extract structured data.
    
    Args:
        text (str): OCR extracted text from receipt
        
    Returns:
        Dict[str, Any]: Extracted receipt data
        
    Raises:
        Exception: If extraction fails
    """
    try:
        logger.info("Parsing receipt text")
        
        # Extract fields using AI
        extracted_data = extract_fields_from_text(text, "receipt")
        
        # Validate the output
        if not validate_receipt_output(extracted_data):
            raise Exception("Receipt output validation failed")
        
        logger.info("Successfully extracted fields from text")
        logger.info("Receipt parsing completed successfully")
        
        return extracted_data
        
    except Exception as e:
        logger.error(f"Failed to extract fields: {e}")
        raise Exception(f"Field extraction failed: {e}")


def get_receipt_summary(data: Dict[str, Any]) -> str:
    """
    Generate a summary of the extracted receipt data.
    
    Args:
        data (Dict[str, Any]): Extracted receipt data
        
    Returns:
        str: Summary string
    """
    try:
        merchant = data.get("MerchantName", "Unknown")
        total = data.get("TotalAmount", "Unknown")
        date = data.get("DateOfPurchase", "Unknown")
        items_count = len(data.get("Items", []))
        payment = data.get("PaymentMethod", "Unknown")
        
        summary = f"Receipt from {merchant} - Total: {total} - Date: {date} - Items: {items_count} - Payment: {payment}"
        return summary
        
    except Exception as e:
        logger.error(f"Error generating receipt summary: {e}")
        return "Receipt summary unavailable" 