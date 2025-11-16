"""Tests for the CLI module."""

import pytest
import json
from pathlib import Path
from config_sanitizer.cli import main
import sys


class TestCLI:
    """Tests for the command-line interface."""
    
    def test_sanitize_json_file(self, tmp_path, monkeypatch, capsys):
        """Test sanitizing a JSON file via CLI."""
        # Create input file
        input_file = tmp_path / "input.json"
        output_file = tmp_path / "output.json"
        
        data = {
            "database": {
                "password": "secret123",
                "host": "localhost"
            }
        }
        
        with open(input_file, 'w') as f:
            json.dump(data, f)
        
        # Mock command-line arguments
        monkeypatch.setattr(sys, 'argv', [
            'config-sanitizer',
            'sanitize',
            str(input_file),
            '-o',
            str(output_file)
        ])
        
        # Run CLI
        main()
        
        # Check output
        captured = capsys.readouterr()
        assert "Successfully processed" in captured.out
        assert output_file.exists()
        
        with open(output_file, 'r') as f:
            result = json.load(f)
        
        assert "secret123" not in str(result)
    
    def test_anonymize_json_file(self, tmp_path, monkeypatch, capsys):
        """Test anonymizing a JSON file via CLI."""
        # Create input file
        input_file = tmp_path / "input.json"
        output_file = tmp_path / "output.json"
        
        data = {
            "email": "user@example.org",
            "ip": "192.168.1.1"
        }
        
        with open(input_file, 'w') as f:
            json.dump(data, f)
        
        # Mock command-line arguments
        monkeypatch.setattr(sys, 'argv', [
            'config-sanitizer',
            'anonymize',
            str(input_file),
            '-o',
            str(output_file),
            '--seed',
            'test-seed'
        ])
        
        # Run CLI
        main()
        
        # Check output
        captured = capsys.readouterr()
        assert "Successfully processed" in captured.out
        assert output_file.exists()
        
        with open(output_file, 'r') as f:
            result = json.load(f)
        
        assert "user@example.org" not in str(result)
        assert "192.168.1.1" not in str(result)
    
    def test_file_not_found(self, monkeypatch, capsys):
        """Test error when file is not found."""
        monkeypatch.setattr(sys, 'argv', [
            'config-sanitizer',
            'sanitize',
            '/nonexistent/file.json'
        ])
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "File not found" in captured.err
    
    def test_no_command(self, monkeypatch, capsys):
        """Test that help is shown when no command is provided."""
        monkeypatch.setattr(sys, 'argv', ['config-sanitizer'])
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
