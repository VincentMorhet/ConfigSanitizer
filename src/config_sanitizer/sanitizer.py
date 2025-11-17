"""Core sanitization and anonymization functions."""

import re
import hashlib
from typing import Dict, Any, List, Pattern


# Patterns to detect sensitive data
SENSITIVE_PATTERNS = {
    "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    "ipv4": re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
    "password": re.compile(r'(?i)(password|pwd|passwd|secret|token|api[_-]?key|auth[_-]?key)\s*[=:]\s*["\']?([^"\'\s]+)["\']?'),
    "api_key": re.compile(r'(?i)(api[_-]?key|token|secret[_-]?key)\s*[=:]\s*["\']?([A-Za-z0-9_\-]{20,})["\']?'),
    "url_with_credentials": re.compile(r'(?i)([a-z]+://[^:]+:[^@]+@[^\s]+)'),
}

# Sensitive key names in dictionaries
SENSITIVE_KEYS = {
    "password", "passwd", "pwd", "secret", "token", 
    "api_key", "apikey", "api-key", "auth_key", "authkey", 
    "auth-key", "private_key", "privatekey", "access_token",
    "refresh_token", "session_token", "bearer_token"
}


def sanitize(data: Any, mask_char: str = "*") -> Any:
    """
    Detect and mask sensitive data in the input.
    
    Args:
        data: Input data to sanitize (str, dict, list, or other types)
        mask_char: Character to use for masking (default: "*")
    
    Returns:
        Sanitized data with sensitive information masked
    """
    if isinstance(data, str):
        return _sanitize_string(data, mask_char)
    elif isinstance(data, dict):
        return _sanitize_dict(data, mask_char)
    elif isinstance(data, list):
        return [sanitize(item, mask_char) for item in data]
    else:
        return data


def _sanitize_dict(data: Dict[str, Any], mask_char: str = "*") -> Dict[str, Any]:
    """Sanitize a dictionary by masking sensitive values."""
    result = {}
    for key, value in data.items():
        # Check if the key itself is sensitive
        if key.lower() in SENSITIVE_KEYS:
            # Mask the value
            if isinstance(value, str):
                result[key] = mask_char * 8
            else:
                result[key] = value
        else:
            # Recursively sanitize the value
            result[key] = sanitize(value, mask_char)
    return result


def _sanitize_string(text: str, mask_char: str = "*") -> str:
    """Sanitize a string by masking sensitive patterns."""
    result = text
    
    # Mask password-like patterns
    password_pattern = SENSITIVE_PATTERNS["password"]
    result = password_pattern.sub(lambda m: f"{m.group(1)}={mask_char * 8}", result)
    
    # Mask API keys
    api_pattern = SENSITIVE_PATTERNS["api_key"]
    result = api_pattern.sub(lambda m: f"{m.group(1)}={mask_char * 20}", result)
    
    # Mask URLs with credentials
    url_pattern = SENSITIVE_PATTERNS["url_with_credentials"]
    result = url_pattern.sub(lambda m: m.group(1).split('@')[0].split('://')[0] + 
                           f"://{mask_char * 8}:{mask_char * 8}@" + 
                           m.group(1).split('@')[1], result)
    
    return result


def anonymize(data: Any, seed: str = "default-seed") -> Any:
    """
    Anonymize data by replacing sensitive information with deterministic fake values.
    
    Args:
        data: Input data to anonymize (str, dict, list, or other types)
        seed: Seed for deterministic generation
    
    Returns:
        Anonymized data with sensitive information replaced by plausible values
    """
    if isinstance(data, str):
        return _anonymize_string(data, seed)
    elif isinstance(data, dict):
        return _anonymize_dict(data, seed)
    elif isinstance(data, list):
        return [anonymize(item, f"{seed}_{i}") for i, item in enumerate(data)]
    else:
        return data


def _anonymize_dict(data: Dict[str, Any], seed: str) -> Dict[str, Any]:
    """Anonymize a dictionary by replacing sensitive values."""
    result = {}
    for key, value in data.items():
        # Check if the key itself is sensitive
        if key.lower() in SENSITIVE_KEYS:
            # Anonymize the value
            if isinstance(value, str):
                result[key] = _generate_fake_password(value, f"{seed}_{key}")
            else:
                result[key] = value
        else:
            # Recursively anonymize the value
            result[key] = anonymize(value, f"{seed}_{key}")
    return result


def _anonymize_string(text: str, seed: str) -> str:
    """Anonymize a string by replacing sensitive patterns with fake values."""
    result = text
    
    # Replace emails
    email_pattern = SENSITIVE_PATTERNS["email"]
    emails = email_pattern.findall(result)
    for email in emails:
        fake_email = _generate_fake_email(email, seed)
        result = result.replace(email, fake_email)
    
    # Replace IPv4 addresses (except network masks and special IPs)
    ipv4_pattern = SENSITIVE_PATTERNS["ipv4"]
    ips = ipv4_pattern.findall(result)
    for ip in ips:
        # Skip network masks and special IPs like 0.0.0.0
        if not _is_network_mask_or_special_ip(ip):
            fake_ip = _generate_fake_ip(ip, seed)
            # Replace only whole-word occurrences to avoid accidental partial replacements
            result = re.sub(r'\b' + re.escape(ip) + r'\b', fake_ip, result)
    
    # Replace password-like patterns
    password_pattern = SENSITIVE_PATTERNS["password"]
    result = password_pattern.sub(
        lambda m: f"{m.group(1)}={_generate_fake_password(m.group(2), seed)}",
        result
    )
    
    # Replace API keys
    api_pattern = SENSITIVE_PATTERNS["api_key"]
    result = api_pattern.sub(
        lambda m: f"{m.group(1)}={_generate_fake_api_key(m.group(2), seed)}",
        result
    )
    
    return result


def _generate_fake_email(original: str, seed: str) -> str:
    """Generate a deterministic fake email based on the original."""
    hash_value = hashlib.md5(f"{original}{seed}".encode()).hexdigest()[:8]
    return f"user{hash_value}@example.com"


def _is_network_mask_or_special_ip(ip: str) -> bool:
    """Check if an IP is a network mask or special IP that should not be anonymized."""
    # Check for 0.0.0.0
    if ip == "0.0.0.0":
        return True
    
    # Check for network masks (IPs starting with 255)
    if ip.startswith("255."):
        return True
    
    return False


def _generate_fake_ip(original: str, seed: str) -> str:
    """Generate a deterministic fake IP address."""
    hash_value = hashlib.md5(f"{original}{seed}".encode()).hexdigest()
    # Build four octets from the hash (each 0-255). Use first octet 10 to keep private range.
    octets = []
    for i in range(0, 8, 2):
        try:
            val = int(hash_value[i:i+2], 16) % 256
        except ValueError:
            val = 0
        octets.append(str(val))
    octets[0] = "10"
    candidate = ".".join(octets)
    if _is_valid_ipv4(candidate):
        return candidate

    # Fallback: construct from a larger int slice to be extra-safe
    int_val = int(hash_value[:8], 16)
    nums = [str((int_val >> shift) & 0xFF) for shift in (24, 16, 8, 0)]
    nums[0] = "10"
    return ".".join(nums)


def _is_valid_ipv4(ip: str) -> bool:
    """Return True if `ip` is a valid IPv4 address (4 octets, each 0-255)."""
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    try:
        for p in parts:
            if not 0 <= int(p) <= 255:
                return False
    except ValueError:
        return False
    return True


def _generate_fake_password(original: str, seed: str) -> str:
    """Generate a deterministic fake password."""
    hash_value = hashlib.md5(f"{original}{seed}".encode()).hexdigest()[:16]
    return f"fake_{hash_value}"


def _generate_fake_api_key(original: str, seed: str) -> str:
    """Generate a deterministic fake API key."""
    hash_value = hashlib.md5(f"{original}{seed}".encode()).hexdigest()
    return f"FAKE_{hash_value[:28].upper()}"
