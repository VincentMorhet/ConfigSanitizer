#!/usr/bin/env python3
"""Run ConfigSanitizer CLI without installing the package.

Usage: python run.py [args...]

This script ensures `src/` is on `sys.path` so the `config_sanitizer`
package can be imported directly from the repository tree.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

def main():
    # Import here so sys.path is already adjusted
    from config_sanitizer.cli import main as cli_main
    cli_main()


if __name__ == "__main__":
    main()
