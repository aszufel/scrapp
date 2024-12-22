"""
Testy jednostkowe dla EmailFinder.
"""

import pytest
from email_finder.email_finder import EmailFinder
from email_finder.utils.validators import is_valid_email, filter_valid_emails

def test_email_validation():
    """Test walidacji adresów email."""
    valid_emails = [
        "test@example.com",
        "user.name@domain.com",
        "user+label@domain.com"
    ]
    invalid_emails = [
        "test@",
        "@domain.com",
        "test@domain",
        "test.domain.com"
    ]
    
    for email in valid_emails:
        assert is_valid_email(email)
        
    for email in invalid_emails:
        assert not is_valid_email(email)

def test_email_extraction():
    """Test wyciągania adresów email z tekstu."""
    finder = EmailFinder()
    text = "Contact us at test@example.com or support@domain.com"
    emails = finder._extract_emails_from_text(text)
    assert len(emails) == 2
    assert "test@example.com" in emails
    assert "support@domain.com" in emails

def test_find_emails_with_context():
    """Test znajdowania maili z kontekstem."""
    finder = EmailFinder()
    # Mockujemy odpowiedź HTTP
    class MockResponse:
        text = """
        <div class="elementor-widget-text-editor">
            <p>Contact our support: support@example.com</p>
        </div>
        """
        def raise_for_status(self):
            pass

    # Podmieniamy metodę get w sesji
    finder.session.get = lambda url, timeout: MockResponse()
    
    results = finder.find_emails_on_page("http://example.com")
    assert len(results) == 1
    email, context = results[0]
    assert email == "support@example.com"
    assert "Contact our support" in context
