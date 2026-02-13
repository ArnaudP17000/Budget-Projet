"""
Validators for the Budget Management Application.
"""
import re
from datetime import date, datetime
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email:
        return True  # Email is optional
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_telephone(telephone: str) -> bool:
    """Validate telephone format."""
    if not telephone:
        return True  # Telephone is optional
    # Accept various formats: +33, 0x xx xx xx xx, etc.
    pattern = r'^[\d\s\+\-\(\)\.]+$'
    return bool(re.match(pattern, telephone)) and len(re.sub(r'\D', '', telephone)) >= 10


def validate_montant(montant: float) -> bool:
    """Validate monetary amount."""
    try:
        return float(montant) >= 0
    except (ValueError, TypeError):
        return False


def validate_annee(annee: int) -> bool:
    """Validate year."""
    try:
        year = int(annee)
        current_year = datetime.now().year
        return 2000 <= year <= current_year + 10
    except (ValueError, TypeError):
        return False


def validate_date(date_str: str) -> bool:
    """Validate date string format (YYYY-MM-DD)."""
    if not date_str:
        return True  # Date is optional
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_date_range(date_debut: Optional[date], date_fin: Optional[date]) -> bool:
    """Validate that end date is after start date."""
    if date_debut and date_fin:
        return date_fin >= date_debut
    return True


def validate_code_postal(code_postal: str) -> bool:
    """Validate French postal code."""
    if not code_postal:
        return True  # Code postal is optional
    return bool(re.match(r'^\d{5}$', code_postal))


def validate_required_field(value: str, field_name: str) -> tuple[bool, str]:
    """Validate that a required field is not empty."""
    if not value or not value.strip():
        return False, f"Le champ '{field_name}' est obligatoire"
    return True, ""


def validate_unique_field(value: str, existing_values: list, field_name: str) -> tuple[bool, str]:
    """Validate that a field value is unique."""
    if value in existing_values:
        return False, f"La valeur '{value}' existe déjà pour le champ '{field_name}'"
    return True, ""


def validate_numero_bc(numero_bc: str) -> bool:
    """Validate bon de commande number format (BC-YYYY-NNNN)."""
    pattern = r'^BC-\d{4}-\d{4}$'
    return bool(re.match(pattern, numero_bc))


def generate_numero_bc(annee: int, sequence: int) -> str:
    """Generate bon de commande number."""
    return f"BC-{annee}-{sequence:04d}"
