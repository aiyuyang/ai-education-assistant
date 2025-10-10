"""
Utility functions for the application
"""
import re
import hashlib
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    result = {
        "is_valid": True,
        "score": 0,
        "feedback": []
    }
    
    if len(password) < 6:
        result["is_valid"] = False
        result["feedback"].append("Password must be at least 6 characters long")
    else:
        result["score"] += 1
    
    if not re.search(r'[A-Z]', password):
        result["feedback"].append("Consider adding uppercase letters")
    else:
        result["score"] += 1
    
    if not re.search(r'[a-z]', password):
        result["feedback"].append("Consider adding lowercase letters")
    else:
        result["score"] += 1
    
    if not re.search(r'\d', password):
        result["feedback"].append("Consider adding numbers")
    else:
        result["score"] += 1
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        result["feedback"].append("Consider adding special characters")
    else:
        result["score"] += 1
    
    return result


def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename"""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    file_extension = original_filename.split('.')[-1] if '.' in original_filename else ''
    
    if file_extension:
        return f"{timestamp}_{unique_id}.{file_extension}"
    else:
        return f"{timestamp}_{unique_id}"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:255-len(ext)-1] + ('.' + ext if ext else '')
    
    return filename


def calculate_pagination_offset(page: int, per_page: int) -> int:
    """Calculate pagination offset"""
    return (page - 1) * per_page


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO string"""
    return dt.isoformat() if dt else None


def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Parse ISO datetime string"""
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except ValueError:
        return None


def generate_hash(data: str) -> str:
    """Generate SHA256 hash of data"""
    return hashlib.sha256(data.encode()).hexdigest()


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text"""
    # Simple keyword extraction (in a real implementation, you might use NLP libraries)
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
    }
    
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Count frequency and return most common
    word_count = {}
    for word in keywords:
        word_count[word] = word_count.get(word, 0) + 1
    
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_words[:max_keywords]]


def validate_json_string(json_str: str) -> bool:
    """Validate if string is valid JSON"""
    try:
        json.loads(json_str)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely load JSON string"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def calculate_time_difference(start_time: datetime, end_time: datetime) -> Dict[str, int]:
    """Calculate time difference between two datetime objects"""
    diff = end_time - start_time
    
    return {
        "days": diff.days,
        "hours": diff.seconds // 3600,
        "minutes": (diff.seconds % 3600) // 60,
        "seconds": diff.seconds % 60,
        "total_seconds": int(diff.total_seconds())
    }


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable string"""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minutes"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} hours {minutes} minutes"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days} days {hours} hours"


def clean_html_tags(html_text: str) -> str:
    """Remove HTML tags from text"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html_text)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text"""
    return re.sub(r'\s+', ' ', text.strip())


def mask_sensitive_data(data: str, mask_char: str = '*', visible_chars: int = 4) -> str:
    """Mask sensitive data (like email, phone numbers)"""
    if len(data) <= visible_chars:
        return mask_char * len(data)
    
    return data[:visible_chars] + mask_char * (len(data) - visible_chars)


def generate_random_string(length: int = 8) -> str:
    """Generate random string"""
    import string
    import random
    
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def is_valid_url(url: str) -> bool:
    """Validate URL format"""
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return pattern.match(url) is not None

