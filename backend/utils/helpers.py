"""
Utility Helper functions for data cleaning, sanitization, and formatting.
"""
import re

def sanitize_string(val: str) -> str:
    if not val:
        return ""
    # Strip dangerous HTML tags or script elements
    cleaned = re.sub(r"<[^>]*?>", "", str(val))
    return cleaned.strip()

def format_currency(val: float) -> str:
    return f"${val:,.2f}"
