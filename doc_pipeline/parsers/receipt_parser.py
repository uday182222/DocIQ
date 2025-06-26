import re
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ReceiptExtractionError(Exception):
    """Raised when receipt field extraction fails"""
    pass

def extract_merchant_name(text: str) -> str:
    """
    Extract merchant/store name from receipt text.
    Looks for common patterns like store names at the top, company names, etc.
    """
    # Common patterns for merchant names
    patterns = [
        # Store names at the beginning of lines (often capitalized)
        r'^([A-Z][A-Z\s&]+(?:STORE|SHOP|MARKET|SUPERMARKET|GROCERY|PHARMACY|RETAIL|OUTLET|MART|CENTER|PLAZA|MALL))',
        # Company names with common suffixes
        r'^([A-Z][A-Z\s&]+(?:INC|LLC|LTD|CORP|CO|COMPANY))',
        # Names in quotes or brackets
        r'["\']([^"\']+)["\']',
        r'\[([^\]]+)\]',
        # Lines that look like store names (all caps, reasonable length)
        r'^([A-Z][A-Z\s&]{2,20})$',
        # Common store name patterns
        r'(WALMART|TARGET|COSTCO|SAFEWAY|KROGER|ALBERTSONS|CVS|WALGREENS|RITE AID|DOLLAR GENERAL|DOLLAR TREE)',
    ]
    
    lines = text.split('\n')
    
    for pattern in patterns:
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                merchant_name = match.group(1) if match.groups() else match.group(0)
                merchant_name = merchant_name.strip()
                if len(merchant_name) >= 2:  # Minimum reasonable length
                    logger.info(f"Extracted merchant name: {merchant_name}")
                    return merchant_name
    
    raise ReceiptExtractionError("Could not extract merchant name from receipt text")

def extract_date(text: str) -> str:
    """
    Extract date from receipt text.
    Looks for various date formats commonly found on receipts.
    """
    # Common date patterns on receipts
    patterns = [
        # MM/DD/YYYY or MM-DD-YYYY
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
        # MM/DD/YY or MM-DD-YY
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})',
        # YYYY-MM-DD
        r'(\d{4})-(\d{1,2})-(\d{1,2})',
        # Month name patterns
        r'(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+(\d{1,2}),?\s+(\d{4})',
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})',
        # Date with time
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\s+(\d{1,2}):(\d{2})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                if len(match.groups()) >= 3:
                    month, day, year = match.groups()[:3]
                    
                    # Handle 2-digit years
                    if len(year) == 2:
                        year = '20' + year if int(year) < 50 else '19' + year
                    
                    # Validate date
                    datetime(int(year), int(month), int(day))
                    
                    date_str = f"{month.zfill(2)}/{day.zfill(2)}/{year}"
                    logger.info(f"Extracted date: {date_str}")
                    return date_str
            except (ValueError, TypeError):
                continue
    
    raise ReceiptExtractionError("Could not extract date from receipt text")

def extract_total(text: str) -> str:
    """
    Extract total amount from receipt text.
    Looks for total, grand total, amount due, etc.
    """
    # Common total patterns
    patterns = [
        # Total: $XX.XX or TOTAL: $XX.XX
        r'(?:TOTAL|GRAND TOTAL|AMOUNT DUE|BALANCE DUE|DUE|OWED)[:\s]*\$?(\d+\.\d{2})',
        # $XX.XX at end of lines (common for totals)
        r'\$(\d+\.\d{2})\s*$',
        # XX.XX with currency symbols
        r'[\$€£¥](\d+\.\d{2})',
        # Just numbers that look like totals (reasonable range)
        r'(\d{1,3}\.\d{2})',
    ]
    
    lines = text.split('\n')
    
    # Look for total in specific order (total lines first, then any amount)
    for pattern in patterns:
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                total = match.group(1)
                # Validate it's a reasonable total amount
                try:
                    amount = float(total)
                    if 0.01 <= amount <= 9999.99:  # Reasonable receipt total range
                        logger.info(f"Extracted total: ${total}")
                        return total
                except ValueError:
                    continue
    
    raise ReceiptExtractionError("Could not extract total amount from receipt text")

def extract_items(text: str) -> List[Dict[str, str]]:
    """
    Extract individual items from receipt text.
    Uses line matching and known structure patterns.
    """
    items = []
    lines = text.split('\n')
    
    # Common item patterns
    item_patterns = [
        # Item name followed by price: "ITEM NAME $XX.XX"
        r'^([A-Za-z\s&]+)\s+\$?(\d+\.\d{2})$',
        # Item with quantity: "QTY ITEM NAME $XX.XX"
        r'^(\d+)\s+([A-Za-z\s&]+)\s+\$?(\d+\.\d{2})$',
        # Item with price and quantity: "ITEM NAME QTY $XX.XX"
        r'^([A-Za-z\s&]+)\s+(\d+)\s+\$?(\d+\.\d{2})$',
        # Simple item-price pattern
        r'^([A-Za-z\s&]{3,30})\s+(\d+\.\d{2})$',
    ]
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue
            
        # Skip header/footer lines
        if any(skip in line.upper() for skip in ['TOTAL', 'SUBTOTAL', 'TAX', 'CHANGE', 'CASH', 'CARD', 'RECEIPT', 'THANK']):
            continue
            
        for pattern in item_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                try:
                    if len(match.groups()) == 2:
                        # Simple item-price pattern
                        item_name = match.group(1).strip()
                        price = match.group(2)
                    elif len(match.groups()) == 3:
                        # Item with quantity
                        if match.group(1).isdigit():
                            # QTY ITEM PRICE pattern
                            quantity = match.group(1)
                            item_name = match.group(2).strip()
                            price = match.group(3)
                        else:
                            # ITEM QTY PRICE pattern
                            item_name = match.group(1).strip()
                            quantity = match.group(2)
                            price = match.group(3)
                    else:
                        continue
                    
                    # Validate price
                    float(price)
                    
                    # Clean up item name
                    item_name = re.sub(r'\s+', ' ', item_name).strip()
                    if len(item_name) >= 2:
                        item = {
                            'name': item_name,
                            'price': price
                        }
                        if 'quantity' in locals():
                            item['quantity'] = quantity
                        
                        items.append(item)
                        logger.info(f"Extracted item: {item}")
                        break
                        
                except (ValueError, IndexError):
                    continue
    
    if not items:
        raise ReceiptExtractionError("Could not extract any items from receipt text")
    
    logger.info(f"Extracted {len(items)} items")
    return items

def extract_payment_method(text: str) -> str:
    """
    Extract payment method from receipt text.
    Looks for common payment method indicators.
    """
    # Common payment method patterns
    patterns = [
        # Card types
        r'(VISA|MASTERCARD|AMEX|AMERICAN EXPRESS|DISCOVER|DEBIT|CREDIT)\s+CARD',
        r'CARD\s+(VISA|MASTERCARD|AMEX|AMERICAN EXPRESS|DISCOVER|DEBIT|CREDIT)',
        # Payment methods
        r'(CASH|CHECK|MONEY ORDER|GIFT CARD|STORE CREDIT)',
        r'(PAYMENT METHOD|PAID BY|TENDER TYPE)[:\s]*(CASH|CARD|CHECK|DEBIT|CREDIT)',
        # Digital payments
        r'(APPLE PAY|GOOGLE PAY|SAMSUNG PAY|PAYPAL|VENMO|ZELLE)',
        # Generic patterns
        r'(DEBIT|CREDIT|CASH|CHECK)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            payment_method = match.group(1) if match.groups() else match.group(0)
            payment_method = payment_method.strip().upper()
            
            # Normalize payment method names
            payment_map = {
                'VISA': 'Visa',
                'MASTERCARD': 'Mastercard', 
                'AMEX': 'American Express',
                'AMERICAN EXPRESS': 'American Express',
                'DISCOVER': 'Discover',
                'DEBIT': 'Debit Card',
                'CREDIT': 'Credit Card',
                'CASH': 'Cash',
                'CHECK': 'Check',
                'APPLE PAY': 'Apple Pay',
                'GOOGLE PAY': 'Google Pay',
                'SAMSUNG PAY': 'Samsung Pay',
                'PAYPAL': 'PayPal',
                'VENMO': 'Venmo',
                'ZELLE': 'Zelle',
            }
            
            payment_method = payment_map.get(payment_method, payment_method.title())
            logger.info(f"Extracted payment method: {payment_method}")
            return payment_method
    
    raise ReceiptExtractionError("Could not extract payment method from receipt text")

def parse_receipt(text: str) -> Dict[str, any]:
    """
    Parse receipt text and extract all fields.
    Raises ReceiptExtractionError if any required field extraction fails.
    """
    logger.info("Parsing receipt text")
    
    try:
        result = {
            'MerchantName': extract_merchant_name(text),
            'DateOfPurchase': extract_date(text),
            'TotalAmount': extract_total(text),
            'Items': extract_items(text),
            'PaymentMethod': extract_payment_method(text)
        }
        
        logger.info(f"Successfully extracted {len(result)} fields")
        return result
        
    except ReceiptExtractionError as e:
        logger.error(f"Receipt parsing failed: {e}")
        raise 