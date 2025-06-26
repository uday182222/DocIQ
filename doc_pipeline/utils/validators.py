def validate_output(data: dict, doc_type: str) -> dict:
    """
    Loads a field schema per doc_type, validates and fills missing optional fields as null,
    ensures required fields are present or raises error.
    Returns the cleaned and validated JSON.
    """
    # Define schemas for each document type
    schemas = {
        "resume": {
            "required": ["FullName"],
            "optional": ["Email", "PhoneNumber", "Skills", "WorkExperience", "Education"],
            "defaults": {
                "Skills": [],
                "WorkExperience": [],
                "Education": []
            }
        },
        "receipt": {
            "required": ["StoreName", "TotalAmount", "LineItems"],
            "optional": ["StoreAddress", "StorePhone", "DateOfPurchase", "TransactionTime", "ReceiptID", "Subtotal", "Tax", "PaymentMethod", "CardLast4Digits", "DiscrepancyWarning"],
            "defaults": {
                "LineItems": [],
                "DiscrepancyWarning": False
            }
        },
        "license": {
            "required": ["Name"],
            "optional": ["DateOfBirth", "LicenseNumber", "IssuingState", "ExpiryDate"],
            "defaults": {}
        }
    }
    
    if doc_type not in schemas:
        raise ValueError(f"Unknown document type: {doc_type}")
    
    schema = schemas[doc_type]
    validated_data = {}
    
    # Check required fields
    for field in schema["required"]:
        if field not in data or data[field] is None:
            raise ValueError(f"Required field '{field}' is missing for {doc_type}")
        validated_data[field] = data[field]
    
    # Handle optional fields
    for field in schema["optional"]:
        if field in data and data[field] is not None:
            validated_data[field] = data[field]
        else:
            # Use default value if specified, otherwise null
            validated_data[field] = schema["defaults"].get(field, None)
    
    # Special validation for receipts
    if doc_type == "receipt":
        # Validate LineItems structure
        if "LineItems" in validated_data and isinstance(validated_data["LineItems"], list):
            for i, item in enumerate(validated_data["LineItems"]):
                if not isinstance(item, dict):
                    raise ValueError(f"LineItem {i} is not a dictionary")
                if "name" not in item or not item["name"]:
                    raise ValueError(f"LineItem {i} missing name")
                if "price" not in item or item["price"] is None:
                    raise ValueError(f"LineItem {i} missing price")
        
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