"""
Formatters for the Budget Management Application.
"""
from datetime import date, datetime
from typing import Optional


def format_date(date_obj: Optional[date]) -> str:
    """Format date object to string."""
    if date_obj is None:
        return ""
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime("%Y-%m-%d")


def format_datetime(datetime_obj: Optional[datetime]) -> str:
    """Format datetime object to string."""
    if datetime_obj is None:
        return ""
    if isinstance(datetime_obj, str):
        return datetime_obj
    return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")


def format_montant(montant: float) -> str:
    """Format monetary amount with currency."""
    return f"{montant:,.2f} €".replace(",", " ")


def format_telephone(telephone: str) -> str:
    """Format telephone number."""
    if not telephone:
        return ""
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, telephone))
    
    # Format as French phone number if 10 digits
    if len(digits) == 10:
        return f"{digits[0:2]} {digits[2:4]} {digits[4:6]} {digits[6:8]} {digits[8:10]}"
    
    return telephone


def format_code_postal(code_postal: str) -> str:
    """Format postal code."""
    if not code_postal:
        return ""
    return code_postal.strip()


def format_email(email: str) -> str:
    """Format email address."""
    if not email:
        return ""
    return email.strip().lower()


def format_size_kb(size_bytes: int) -> str:
    """Format file size in KB."""
    return f"{size_bytes / 1024:.2f} KB"


def format_percentage(value: float, total: float) -> str:
    """Format percentage."""
    if total == 0:
        return "0 %"
    percentage = (value / total) * 100
    return f"{percentage:.1f} %"


def parse_date(date_str: str) -> Optional[date]:
    """Parse date string to date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_datetime(datetime_str: str) -> Optional[datetime]:
    """Parse datetime string to datetime object."""
    if not datetime_str:
        return None
    try:
        return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        # Try alternative format
        try:
            return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            return None


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to maximum length."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
