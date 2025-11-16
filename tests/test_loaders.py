"""Tests for the loaders module."""

import pytest
import tempfile
import json
from pathlib import Path
from config_sanitizer.loaders import (
    load_file, save_file,
    load_json, save_json,
    load_yaml, save_yaml,
    load_ini, save_ini,
    load_env, save_env,
    load_txt, save_txt
)


class TestLoaders:
    """Tests for file loaders."""
    
    def test_load_save_json(self, tmp_path):
        """Test loading and saving JSON files."""
        data = {"name": "test", "value": 123}
        filepath = tmp_path / "test.json"
        
        save_json(str(filepath), data)
        loaded = load_json(str(filepath))
        
        assert loaded == data
    
    def test_load_save_yaml(self, tmp_path):
        """Test loading and saving YAML files."""
        data = {"name": "test", "items": ["a", "b", "c"]}
        filepath = tmp_path / "test.yaml"
        
        save_yaml(str(filepath), data)
        loaded = load_yaml(str(filepath))
        
        assert loaded == data
    
    def test_load_save_ini(self, tmp_path):
        """Test loading and saving INI files."""
        data = {
            "section1": {"key1": "value1", "key2": "value2"},
            "section2": {"key3": "value3"}
        }
        filepath = tmp_path / "test.ini"
        
        save_ini(str(filepath), data)
        loaded = load_ini(str(filepath))
        
        assert loaded == data
    
    def test_load_save_env(self, tmp_path):
        """Test loading and saving ENV files."""
        data = {"VAR1": "value1", "VAR2": "value2"}
        filepath = tmp_path / "test.env"
        
        save_env(str(filepath), data)
        loaded = load_env(str(filepath))
        
        assert loaded == data
    
    def test_load_save_txt(self, tmp_path):
        """Test loading and saving TXT files."""
        data = "This is a test\nWith multiple lines"
        filepath = tmp_path / "test.txt"
        
        save_txt(str(filepath), data)
        loaded = load_txt(str(filepath))
        
        assert loaded == data
    
    def test_load_file_json(self, tmp_path):
        """Test generic load_file with JSON."""
        data = {"test": "data"}
        filepath = tmp_path / "test.json"
        
        with open(filepath, 'w') as f:
            json.dump(data, f)
        
        loaded = load_file(str(filepath))
        assert loaded == data
    
    def test_load_file_yml_extension(self, tmp_path):
        """Test generic load_file with .yml extension."""
        data = {"test": "data"}
        filepath = tmp_path / "test.yml"
        
        save_yaml(str(filepath), data)
        loaded = load_file(str(filepath))
        
        assert loaded == data
    
    def test_save_file_json(self, tmp_path):
        """Test generic save_file with JSON."""
        data = {"test": "data"}
        filepath = tmp_path / "test.json"
        
        save_file(str(filepath), data)
        
        with open(filepath, 'r') as f:
            loaded = json.load(f)
        
        assert loaded == data
    
    def test_unsupported_format_load(self, tmp_path):
        """Test that unsupported format raises error."""
        filepath = tmp_path / "test.xyz"
        filepath.touch()
        
        with pytest.raises(ValueError, match="Unsupported file format"):
            load_file(str(filepath))
    
    def test_unsupported_format_save(self, tmp_path):
        """Test that unsupported format raises error on save."""
        filepath = tmp_path / "test.xyz"
        
        with pytest.raises(ValueError, match="Unsupported file format"):
            save_file(str(filepath), {"test": "data"})
