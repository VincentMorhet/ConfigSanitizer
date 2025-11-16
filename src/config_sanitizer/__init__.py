"""ConfigSanitizer - A tool to sanitize and anonymize configuration files."""

from .sanitizer import sanitize, anonymize

__version__ = "0.1.0"
__all__ = ["sanitize", "anonymize"]
