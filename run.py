#!/usr/bin/env python3
"""Run ConfigSanitizer CLI without installing the package.

Usage:
  python run.py sanitize input.file -o out.file
  python run.py anonymize input.file -o out.file --seed my-seed

This script ensures `src/` is on `sys.path` so the package can be imported
directly from the repository checkout.
"""
import os
import sys


def _add_src_to_path():
    """Add the repository `src/` directory to sys.path (front) if not present."""
    repo_root = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(repo_root, "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)


def main():
    _add_src_to_path()
    # Import here so sys.path is already updated
    from config_sanitizer.cli import main as cli_main
    cli_main()


if __name__ == "__main__":
    main()
