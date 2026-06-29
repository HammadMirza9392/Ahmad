"""
Helper Utilities
Common functions used across the application.
"""
import re
import uuid
import json
from datetime import datetime
from markupsafe import Markup
import markdown
import bleach


def generate_slug(text):
    """Convert text to URL-safe slug."""
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug


def generate_unique_filename(original_filename):
    """Generate a unique filename while preserving the extension."""
    ext = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else ''
    unique_name = f"{uuid.uuid4().hex}"
    return f"{unique_name}.{ext}" if ext else unique_name


def format_file_size(size_bytes):
    """Convert bytes to human-readable format."""
    if size_bytes is None:
        return '0 B'
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def render_markdown(text):
    """Safely render Markdown to HTML."""
    if not text:
        return ''
    allowed_tags = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr',
        'strong', 'em', 'b', 'i', 'u', 'code', 'pre', 'blockquote',
        'ul', 'ol', 'li', 'a', 'img', 'table', 'thead', 'tbody',
        'tr', 'th', 'td', 'span', 'div', 'sup', 'sub',
    ]
    allowed_attrs = {
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'code': ['class'],
        'pre': ['class'],
        'span': ['class'],
        'div': ['class'],
        'td': ['align'],
        'th': ['align'],
    }
    html = markdown.markdown(text, extensions=['extra', 'codehilite', 'tables', 'toc'])
    clean = bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs)
    return Markup(clean)


def truncate_text(text, length=200):
    """Truncate text to specified length with ellipsis."""
    if not text or len(text) <= length:
        return text or ''
    return text[:length].rsplit(' ', 1)[0] + '...'


def safe_json_loads(text, default=None):
    """Safely parse JSON string."""
    try:
        return json.loads(text) if text else default
    except (json.JSONDecodeError, TypeError):
        return default


def time_ago(dt):
    """Human-readable relative time (e.g., '5 minutes ago')."""
    if not dt:
        return ''
    now = datetime.utcnow()
    diff = now - dt
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return 'just now'
    elif seconds < 3600:
        mins = seconds // 60
        return f"{mins} minute{'s' if mins != 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        return dt.strftime('%b %d, %Y')


def get_device_type(user_agent):
    """Determine device type from user-agent string."""
    if not user_agent:
        return 'unknown'
    ua = user_agent.lower()
    if any(kw in ua for kw in ['mobile', 'android', 'iphone', 'ipod']):
        return 'mobile'
    elif any(kw in ua for kw in ['ipad', 'tablet']):
        return 'tablet'
    return 'desktop'
