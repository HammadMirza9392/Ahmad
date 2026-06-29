"""
Input Validators
Server-side validation for forms and API inputs.
"""
import re


def validate_email(email):
    """Validate email format."""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password):
    """Validate password strength. Returns (is_valid, message)."""
    if not password or len(password) < 8:
        return False, 'Password must be at least 8 characters long.'
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter.'
    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter.'
    if not re.search(r'\d', password):
        return False, 'Password must contain at least one digit.'
    return True, 'Password is strong.'


def validate_phone(phone):
    """Validate phone number format."""
    if not phone:
        return True  # optional field
    pattern = r'^\+?[\d\s-]{7,20}$'
    return bool(re.match(pattern, phone))


def sanitize_input(text):
    """Strip dangerous characters from user input."""
    if not text:
        return ''
    text = text.strip()
    # Remove null bytes
    text = text.replace('\x00', '')
    return text


def validate_file_extension(filename, allowed_extensions):
    """Check if file extension is allowed."""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[-1].lower()
    return ext in allowed_extensions
