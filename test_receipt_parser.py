#!/usr/bin/env python3
"""
Test script for receipt parser with validation capabilities
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add the doc_pipeline directory to the Python path
sys.path.append('doc_pipeline')

from llm.llm_client import extract_fields_from_text


def load_sample_ocr_text() -> str:
    """
    Load a sample OCR text string from a receipt.
    """
    sample_text = """
    WALMART STORE #1234
    1234 Main Street, Anytown, CA 90210
    Phone: (555) 123-4567
    
    Receipt #987654321
    Date: 12/15/2023
    Time: 14:30:25
    
    ITEMS:
    2x Milk $4.98
    Bread $3.50
    Eggs 12ct $5.99
    Bananas @ 0.59/lb 2.5lb $1.48
    Chicken Breast $12.99
    
    SUBTOTAL: $28.94
    TAX: $2.32
    TOTAL: $31.26
    
    Payment Method: Credit Card
    Card: **** **** **** 1234
    
    Thank you for shopping at Walmart!
    """
    return sample_text.strip()


def load_receipt_prompt() -> str:
    """
    Load the receipt_extraction.txt prompt from the prompts directory.
    """
    prompt_path = Path("doc_pipeline/prompts/receipt_extraction.txt")
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Receipt prompt not found: {prompt_path}")
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def validate_receipt_data(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate receipt data for consistency and completeness.
    Returns (is_valid, list_of_issues)
    """
    issues = []
    
    # Check required fields
    if "StoreName" not in data or data["StoreName"] is None:
        issues.append("Missing required field: StoreName")
    
    if "TotalAmount" not in data or data["TotalAmount"] is None:
        issues.append("Missing required field: TotalAmount")
    
    if "LineItems" not in data or not isinstance(data["LineItems"], list):
        issues.append("Missing or invalid LineItems array")
        return False, issues
    
    if len(data["LineItems"]) == 0:
        issues.append("LineItems array is empty")
    
    # Validate line items
    total_items_price = 0.0
    for i, item in enumerate(data["LineItems"]):
        if not isinstance(item, dict):
            issues.append(f"LineItem {i} is not a dictionary")
            continue
            
        # Check required item fields
        if "name" not in item or not item["name"]:
            issues.append(f"LineItem {i} missing name")
        
        if "price" not in item or item["price"] is None:
            issues.append(f"LineItem {i} missing price")
        else:
            total_items_price += float(item["price"])
    
    # Check for discrepancy warning
    if data.get("TotalAmount") and total_items_price > 0:
        total_amount = float(data["TotalAmount"])
        discrepancy_percentage = abs(total_items_price - total_amount) / total_amount
        
        if discrepancy_percentage > 0.02:  # 2% tolerance
            issues.append(f"Discrepancy detected: Sum of items (${total_items_price:.2f}) ≠ TotalAmount (${total_amount:.2f}) - {discrepancy_percentage:.1%} difference")
            
            # Check if DiscrepancyWarning is set
            if not data.get("DiscrepancyWarning", False):
                issues.append("DiscrepancyWarning should be set to true")
    
    # Validate subtotal + tax = total (if both are present)
    subtotal = data.get("Subtotal")
    tax = data.get("Tax")
    total = data.get("TotalAmount")
    
    if subtotal is not None and tax is not None and total is not None:
        expected_total = float(subtotal) + float(tax)
        if abs(expected_total - float(total)) > 0.01:
            issues.append(f"Subtotal + Tax ≠ Total ({subtotal} + {tax} ≠ {total})")
    
    return len(issues) == 0, issues


def test_receipt_parser():
    """
    Main test function for receipt parser.
    """
    print("=== Receipt Parser Test ===")
    
    try:
        # 1. Load sample OCR text
        print("1. Loading sample OCR text...")
        ocr_text = load_sample_ocr_text()
        print(f"   OCR Text length: {len(ocr_text)} characters")
        print(f"   Sample text: {ocr_text[:100]}...")
        
        # 2. Load receipt extraction prompt
        print("\n2. Loading receipt extraction prompt...")
        prompt = load_receipt_prompt()
        print(f"   Prompt loaded successfully")
        
        # 3. Call extract_fields_from_text()
        print("\n3. Calling extract_fields_from_text()...")
        result = extract_fields_from_text(ocr_text, prompt)
        
        # 4. Print the resulting JSON object
        print("\n4. Extracted JSON result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 5. Validate the result
        print("\n5. Validating receipt data...")
        is_valid, issues = validate_receipt_data(result)
        
        if is_valid:
            print("   ✓ Receipt data is valid")
        else:
            print("   ✗ Receipt data has issues:")
            for issue in issues:
                print(f"     - {issue}")
        
        # 6. Save output to file
        print("\n6. Saving output to file...")
        output_dir = Path("test/output/shop_receipts")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "receipt_test_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"   Output saved to: {output_file}")
        
        # 7. Summary
        print("\n7. Summary:")
        print(f"   Store Name: {result.get('StoreName', 'N/A')}")
        print(f"   Store Address: {result.get('StoreAddress', 'N/A')}")
        print(f"   Date of Purchase: {result.get('DateOfPurchase', 'N/A')}")
        print(f"   Receipt ID: {result.get('ReceiptID', 'N/A')}")
        print(f"   Number of Items: {len(result.get('LineItems', []))}")
        print(f"   Total Amount: ${result.get('TotalAmount', 'N/A')}")
        print(f"   Subtotal: ${result.get('Subtotal', 'N/A')}")
        print(f"   Tax: ${result.get('Tax', 'N/A')}")
        print(f"   Payment Method: {result.get('PaymentMethod', 'N/A')}")
        print(f"   Card Last 4: {result.get('CardLast4Digits', 'N/A')}")
        print(f"   Discrepancy Warning: {result.get('DiscrepancyWarning', False)}")
        
        print("\n=== Test completed successfully! ===")
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_receipt_parser() 