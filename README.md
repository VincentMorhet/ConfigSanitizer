# ConfigSanitizer

A Python CLI tool to sanitize and anonymize configuration files by detecting and masking/replacing sensitive data.

## Features

- **Sanitize**: Detect and mask sensitive data (passwords, API keys, tokens) with asterisks
- **Anonymize**: Replace sensitive data with deterministic, plausible fake values (emails, IPs, passwords)
- **Multi-format support**: Works with TXT, JSON, YAML, INI, and ENV files
- **Deterministic**: Anonymization produces the same output for the same input and seed
- **Simple API**: Easy-to-use `sanitize()` and `anonymize()` functions

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e .[dev]
```

## Usage

### Command Line Interface

#### Sanitize (mask sensitive data)

```bash
# Sanitize a JSON file
config-sanitizer sanitize config.json -o config_sanitized.json

# Sanitize a YAML file
config-sanitizer sanitize config.yaml -o config_sanitized.yaml

# Sanitize and print to stdout
config-sanitizer sanitize config.env

# Use custom mask character
config-sanitizer sanitize config.json -o output.json --mask-char X
```

#### Anonymize (replace with fake data)

```bash
# Anonymize a JSON file
config-sanitizer anonymize config.json -o config_anonymized.json

# Anonymize with custom seed for deterministic results
config-sanitizer anonymize config.yaml -o config_anon.yaml --seed my-secret-seed

# Anonymize and print to stdout
config-sanitizer anonymize config.env
```

### Python API

```python
from config_sanitizer import sanitize, anonymize

# Sanitize data (mask sensitive values)
data = {
    "database": {
        "host": "localhost",
        "password": "secret123"
    }
}
sanitized = sanitize(data)
# Result: {"database": {"host": "localhost", "password": "********"}}

# Anonymize data (replace with fake values)
anonymized = anonymize(data, seed="my-seed")
# Result: {"database": {"host": "localhost", "password": "fake_abc123..."}}

# Works with strings too
text = "password=secret123 email=user@example.com ip=192.168.1.1"
sanitized_text = sanitize(text)
anonymized_text = anonymize(text)
```

## What Data is Detected?

ConfigSanitizer automatically detects and handles:

- **Passwords and secrets**: Keys named `password`, `passwd`, `pwd`, `secret`, `token`, `api_key`, etc.
- **Email addresses**: Standard email format (user@domain.com)
- **IP addresses**: IPv4 addresses
- **API keys and tokens**: Long alphanumeric strings in key-value patterns
- **URLs with credentials**: URLs containing username:password@host

## Supported File Formats

- **JSON** (.json)
- **YAML** (.yaml, .yml)
- **INI** (.ini)
- **ENV** (.env)
- **TXT** (.txt)

## Project Structure

```
ConfigSanitizer/
├── src/
│   └── config_sanitizer/
│       ├── __init__.py
│       ├── sanitizer.py    # Core sanitize() and anonymize() functions
│       ├── loaders.py      # File format loaders and savers
│       └── cli.py          # Command-line interface
├── tests/
│   ├── test_sanitizer.py   # Tests for sanitization
│   ├── test_loaders.py     # Tests for file loaders
│   └── test_cli.py         # Tests for CLI
├── pyproject.toml
└── README.md
```

## Development

Run tests:
```bash
pytest tests/
```

Run tests with coverage:
```bash
pytest tests/ --cov=config_sanitizer
```

## Examples

### Example 1: Sanitizing a configuration file

Input (`config.json`):
```json
{
  "database": {
    "host": "localhost",
    "password": "super_secret_password"
  },
  "api": {
    "token": "1234567890abcdefghijklmnopqrstuvwxyz",
    "email": "contact@company.com"
  }
}
```

Command:
```bash
config-sanitizer sanitize config.json -o sanitized.json
```

Output (`sanitized.json`):
```json
{
  "database": {
    "host": "localhost",
    "password": "********"
  },
  "api": {
    "token": "********",
    "email": "contact@company.com"
  }
}
```

### Example 2: Anonymizing with deterministic fake data

Command:
```bash
config-sanitizer anonymize config.json -o anonymized.json --seed my-seed
```

Output (`anonymized.json`):
```json
{
  "database": {
    "host": "localhost",
    "password": "fake_acf4c429ed0b584b"
  },
  "api": {
    "token": "fake_a291b37b17c6f547",
    "email": "userd3c3f93c@example.com"
  }
}
```

## License

MIT

