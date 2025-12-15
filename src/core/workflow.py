"""
Workflow instructions for specific tasks.
"""

import re
from typing import Dict


def parse_query(query: str) -> Dict[str, any]:
    """
    Parse natural language query to extract configuration parameters.
    
    Args:
        query: Natural language query
    
    Returns:
        Dictionary with extracted parameters
    """
    query_lower = query.lower()
    
    result = {
        "quantity": None,
        "product": None,
        "ram": None,
        "storage": None,
        "warranty": None,
        "customer_type": None,
        "region": None,
    }
    
    # Extract quantity
    qty_match = re.search(r'(\d+)\s*(?:thinkpad|units?|laptops?|x1)', query_lower)
    if qty_match:
        result["quantity"] = int(qty_match.group(1))
    
    # Extract product
    if "thinkpad" in query_lower or "x1 carbon" in query_lower:
        result["product"] = "ThinkPad X1 Carbon"
    
    # Extract RAM
    ram_match = re.search(r'(\d+)\s*gb\s*ram', query_lower)
    if ram_match:
        result["ram"] = f"{ram_match.group(1)}GB"
    
    # Extract storage
    storage_match = re.search(r'(\d+)\s*tb\s*ssd', query_lower)
    if storage_match:
        result["storage"] = f"{storage_match.group(1)}TB SSD"
    
    # Extract warranty
    warranty_match = re.search(r'(\d+)[\s-]?year', query_lower)
    if warranty_match:
        result["warranty"] = f"{warranty_match.group(1)}-year"
    
    # Extract customer type
    if "healthcare" in query_lower:
        result["customer_type"] = "healthcare"
    elif "enterprise" in query_lower:
        result["customer_type"] = "enterprise"
    
    # Extract region
    if "texas" in query_lower:
        result["region"] = "Texas"
    
    return result


def get_thinkpad_workflow_instructions(query: str) -> str:
    """
    Generate step-by-step workflow instructions for ThinkPad configuration.
    
    Args:
        query: The user's query
    
    Returns:
        Workflow instructions string
    """
    params = parse_query(query)
    
    instructions = "\n\n=== THINKPAD X1 CARBON CONFIGURATOR WORKFLOW ===\n"
    instructions += "Follow these steps in order. Find the actual coordinates from the screenshot for each step:\n\n"
    
    step_num = 1
    
    if params.get("ram"):
        instructions += f"STEP {step_num}: Find and click on the Memory/RAM section. Look for options showing RAM capacity.\n"
        step_num += 1
        instructions += f"STEP {step_num}: Select the {params['ram']} RAM option. Click on the option that shows {params['ram']}.\n"
        step_num += 1
    
    if params.get("storage"):
        instructions += f"STEP {step_num}: Find and click on the Storage/SSD section. Look for storage capacity options.\n"
        step_num += 1
        instructions += f"STEP {step_num}: Select the {params['storage']} option. Click on the option that shows {params['storage']}.\n"
        step_num += 1
    
    if params.get("warranty"):
        instructions += f"STEP {step_num}: Find and click on the Warranty/Support section. Look for warranty duration options.\n"
        step_num += 1
        instructions += f"STEP {step_num}: Select the {params['warranty']} warranty option.\n"
        step_num += 1
    
    if params.get("quantity"):
        instructions += f"STEP {step_num}: Find the quantity field (may be labeled 'Qty', 'Quantity', or have a number input). Click on it and type: {params['quantity']}\n"
        step_num += 1
    
    instructions += f"STEP {step_num}: After all configurations are complete, find and click the 'Add to Cart' button. "
    instructions += "It may be labeled as 'Add to Cart', 'Add to Bag', 'Add', or similar. "
    instructions += "Look for a prominent button, usually at the bottom or side of the configurator.\n"
    step_num += 1
    
    instructions += f"STEP {step_num}: After clicking 'Add to Cart', wait for the page to update. "
    instructions += "Then look for the final price on the page. It may be labeled as 'Total', 'Price', 'Your Price', 'Cart Total', or shown in a summary/cart section. "
    instructions += "Extract the price value, quantity, and configuration details.\n\n"
    
    instructions += "IMPORTANT:\n"
    instructions += "- Scroll down if needed to find each section (Memory, Storage, Warranty, Quantity)\n"
    instructions += "- Wait for dropdowns/options to appear after clicking\n"
    instructions += "- Use coordinates from the screenshot - do not guess\n"
    instructions += "- When done, use the 'done' action with a structured result containing price and status\n"
    
    return instructions


def extract_result_info(result_text: str) -> Dict[str, any]:
    """
    Extract structured information from the result text.
    
    Args:
        result_text: The result string from the 'done' action
    
    Returns:
        Dictionary with extracted information
    """
    import json
    import re
    
    info = {
        "status": "unknown",
        "price": None,
        "unit_price": None,
        "total_price": None,
        "quantity": None,
        "configuration": {},
        "message": result_text,
    }
    
    result_lower = result_text.lower()
    
    # Try to extract price
    price_patterns = [
        r'\$[\d,]+\.?\d*',
        r'[\d,]+\.?\d*\s*dollars?',
        r'price[:\s]+[\$]?([\d,]+\.?\d*)',
        r'total[:\s]+[\$]?([\d,]+\.?\d*)',
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, result_text, re.IGNORECASE)
        if match:
            price_str = match.group(0) if match.lastindex is None else match.group(1)
            price_str = price_str.replace('$', '').replace(',', '').strip()
            try:
                info["price"] = float(price_str)
                info["total_price"] = float(price_str)
            except ValueError:
                pass
            break
    
    # Try to extract quantity
    qty_match = re.search(r'quantity[:\s]+(\d+)', result_lower)
    if qty_match:
        try:
            info["quantity"] = int(qty_match.group(1))
        except ValueError:
            pass
    
    # Determine status
    if "success" in result_lower or "complete" in result_lower or "done" in result_lower:
        info["status"] = "success"
    elif "fail" in result_lower or "error" in result_lower or "unable" in result_lower:
        info["status"] = "failed"
    elif info["price"] is not None:
        info["status"] = "success"
    
    # Try to parse as JSON if it looks like JSON
    try:
        json_data = json.loads(result_text)
        if isinstance(json_data, dict):
            info.update(json_data)
    except (json.JSONDecodeError, ValueError):
        pass
    
    return info

