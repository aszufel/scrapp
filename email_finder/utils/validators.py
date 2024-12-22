"""
Moduł zawierający funkcje walidacyjne.
"""

import re
from typing import List

def is_valid_email(email: str) -> bool:
    """
    Sprawdza, czy podany ciąg znaków jest poprawnym adresem email.
    
    Args:
        email (str): Adres email do sprawdzenia
        
    Returns:
        bool: True jeśli email jest poprawny, False w przeciwnym razie
    """
    pattern = r'^[a-zA-Z0-9._%+-]{2,}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def filter_valid_emails(emails: List[str]) -> List[str]:
    """
    Filtruje listę, pozostawiając tylko poprawne adresy email.
    
    Args:
        emails (List[str]): Lista adresów email
        
    Returns:
        List[str]: Lista poprawnych adresów email
    """
    return [email for email in emails if is_valid_email(email)]
