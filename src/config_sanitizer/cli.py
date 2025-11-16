"""Command-line interface for ConfigSanitizer."""

import argparse
import sys
from pathlib import Path
from .loaders import load_file, save_file
from .sanitizer import sanitize, anonymize


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Sanitize and anonymize configuration files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sanitize a file (mask sensitive data)
  config-sanitizer sanitize config.json -o config_sanitized.json
  
  # Anonymize a file (replace with fake values)
  config-sanitizer anonymize config.yaml -o config_anonymized.yaml
  
  # Specify custom seed for anonymization
  config-sanitizer anonymize config.env -o config_anon.env --seed my-seed
  
Supported file formats: .txt, .json, .yaml, .yml, .ini, .env
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Sanitize command
    sanitize_parser = subparsers.add_parser(
        'sanitize',
        help='Mask sensitive data in configuration files'
    )
    sanitize_parser.add_argument(
        'input',
        help='Input file path'
    )
    sanitize_parser.add_argument(
        '-o', '--output',
        help='Output file path (default: print to stdout)'
    )
    sanitize_parser.add_argument(
        '--mask-char',
        default='*',
        help='Character to use for masking (default: *)'
    )
    
    # Anonymize command
    anonymize_parser = subparsers.add_parser(
        'anonymize',
        help='Replace sensitive data with deterministic fake values'
    )
    anonymize_parser.add_argument(
        'input',
        help='Input file path'
    )
    anonymize_parser.add_argument(
        '-o', '--output',
        help='Output file path (default: print to stdout)'
    )
    anonymize_parser.add_argument(
        '--seed',
        default='default-seed',
        help='Seed for deterministic generation (default: default-seed)'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        # Load input file
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        
        data = load_file(args.input)
        
        # Process data
        if args.command == 'sanitize':
            result = sanitize(data, mask_char=args.mask_char)
        elif args.command == 'anonymize':
            result = anonymize(data, seed=args.seed)
        else:
            print(f"Error: Unknown command: {args.command}", file=sys.stderr)
            sys.exit(1)
        
        # Output result
        if args.output:
            save_file(args.output, result)
            print(f"Successfully processed {args.input} -> {args.output}")
        else:
            # Print to stdout
            if isinstance(result, str):
                print(result)
            else:
                import json
                print(json.dumps(result, indent=2, ensure_ascii=False))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
