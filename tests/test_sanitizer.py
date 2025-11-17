"""Tests for the sanitizer module."""

import pytest
from config_sanitizer.sanitizer import sanitize, anonymize


class TestSanitize:
    """Tests for the sanitize function."""
    
    def test_sanitize_string_with_password(self):
        """Test sanitizing a string with password."""
        text = "password=my_secret_pass"
        result = sanitize(text)
        assert "my_secret_pass" not in result
        assert "password=********" in result
    
    def test_sanitize_string_with_api_key(self):
        """Test sanitizing a string with API key."""
        text = "api_key=1234567890abcdefghijklmnopqrstuvwxyz"
        result = sanitize(text)
        assert "1234567890abcdefghijklmnopqrstuvwxyz" not in result
        assert "api_key=" in result
        assert "********" in result
    
    def test_sanitize_dict(self):
        """Test sanitizing a dictionary."""
        data = {
            "database": {
                "host": "localhost",
                "password": "secret123"
            },
            "api": {
                "token": "very_long_api_token_here_1234567890"
            }
        }
        result = sanitize(data)
        assert isinstance(result, dict)
        assert result["database"]["password"] == "********"
        assert result["api"]["token"] == "********"
        assert result["database"]["host"] == "localhost"
    
    def test_sanitize_list(self):
        """Test sanitizing a list."""
        data = ["password=secret", "user=admin", "token=abcdefghijklmnopqrstuvwxyz123456"]
        result = sanitize(data)
        assert isinstance(result, list)
        assert len(result) == 3
        assert "secret" not in result[0]
    
    def test_sanitize_with_custom_mask_char(self):
        """Test sanitizing with custom mask character."""
        text = "password=secret"
        result = sanitize(text, mask_char='X')
        assert "XXXXXXXX" in result
    
    def test_sanitize_preserves_other_data(self):
        """Test that sanitize preserves non-sensitive data."""
        data = {
            "name": "John Doe",
            "age": 30,
            "city": "Paris"
        }
        result = sanitize(data)
        assert result == data


class TestAnonymize:
    """Tests for the anonymize function."""
    
    def test_anonymize_email(self):
        """Test anonymizing an email address."""
        text = "Contact: john.doe@example.org"
        result = anonymize(text)
        assert "john.doe@example.org" not in result
        assert "@example.com" in result
        assert "user" in result
    
    def test_anonymize_ip_address(self):
        """Test anonymizing an IP address."""
        text = "Server IP: 192.168.1.100"
        result = anonymize(text)
        assert "192.168.1.100" not in result
        assert "10." in result  # Should be in private range
    
    def test_anonymize_password(self):
        """Test anonymizing a password."""
        text = "password=my_secret"
        result = anonymize(text)
        assert "my_secret" not in result
        assert "password=fake_" in result
    
    def test_anonymize_deterministic(self):
        """Test that anonymization is deterministic."""
        text = "email@example.com"
        result1 = anonymize(text, seed="test-seed")
        result2 = anonymize(text, seed="test-seed")
        assert result1 == result2
    
    def test_anonymize_different_seeds(self):
        """Test that different seeds produce different results."""
        text = "email@example.com"
        result1 = anonymize(text, seed="seed1")
        result2 = anonymize(text, seed="seed2")
        assert result1 != result2
    
    def test_anonymize_dict(self):
        """Test anonymizing a dictionary."""
        data = {
            "email": "admin@company.com",
            "server": "192.168.1.1"
        }
        result = anonymize(data)
        assert isinstance(result, dict)
        assert "admin@company.com" not in str(result)
        assert "192.168.1.1" not in str(result)
    
    def test_anonymize_list(self):
        """Test anonymizing a list."""
        data = ["user@example.com", "192.168.1.1"]
        result = anonymize(data)
        assert isinstance(result, list)
        assert len(result) == 2
        assert "user@example.com" not in result[0]
        assert "192.168.1.1" not in result[1]
    
    def test_anonymize_preserves_structure(self):
        """Test that anonymize preserves data structure."""
        data = {
            "users": [
                {"name": "Alice", "email": "alice@example.com"},
                {"name": "Bob", "email": "bob@example.com"}
            ],
            "config": {
                "host": "10.0.0.1",
                "port": 8080
            }
        }
        result = anonymize(data)
        assert isinstance(result, dict)
        assert "users" in result
        assert "config" in result
        assert len(result["users"]) == 2
        assert result["config"]["port"] == 8080
    
    def test_anonymize_preserves_network_masks(self):
        """Test that network masks are not anonymized."""
        text = "netmask=255.255.255.0"
        result = anonymize(text)
        assert "255.255.255.0" in result
        
        text2 = "mask=255.255.255.255"
        result2 = anonymize(text2)
        assert "255.255.255.255" in result2
        
        text3 = "subnet=255.255.0.0"
        result3 = anonymize(text3)
        assert "255.255.0.0" in result3
    
    def test_anonymize_preserves_zero_ip(self):
        """Test that 0.0.0.0 IP is not anonymized."""
        text = "bind=0.0.0.0"
        result = anonymize(text)
        assert "0.0.0.0" in result
    
    def test_anonymize_normal_ips_still_works(self):
        """Test that normal IPs are still anonymized."""
        text = "server=192.168.1.1"
        result = anonymize(text)
        assert "192.168.1.1" not in result
        assert "10." in result

    def test_anonymize_generates_valid_ipv4(self):
        """Anonymized IPs must be valid IPv4 addresses (each octet 0-255)."""
        text = "server=123.45.67.89"
        result = anonymize(text)
        import re
        m = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", result)
        assert m, "No IP found in anonymized result"
        ip = m.group(0)
        parts = ip.split('.')
        assert len(parts) == 4
        for p in parts:
            assert 0 <= int(p) <= 255
