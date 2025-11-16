"""File loaders for different configuration formats."""

import json
import yaml
import configparser
from pathlib import Path
from typing import Any, Dict
from dotenv import dotenv_values


def load_file(filepath: str) -> Any:
    """
    Load a configuration file based on its extension.
    
    Args:
        filepath: Path to the file to load
    
    Returns:
        Loaded data in appropriate format
    
    Raises:
        ValueError: If file format is not supported
    """
    path = Path(filepath)
    extension = path.suffix.lower()
    
    if extension == '.json':
        return load_json(filepath)
    elif extension in ['.yaml', '.yml']:
        return load_yaml(filepath)
    elif extension == '.ini':
        return load_ini(filepath)
    elif extension == '.env':
        return load_env(filepath)
    elif extension == '.txt':
        return load_txt(filepath)
    else:
        raise ValueError(f"Unsupported file format: {extension}")


def load_json(filepath: str) -> Dict[str, Any]:
    """Load a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_yaml(filepath: str) -> Any:
    """Load a YAML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_ini(filepath: str) -> Dict[str, Dict[str, str]]:
    """Load an INI file."""
    config = configparser.ConfigParser()
    config.read(filepath, encoding='utf-8')
    
    result = {}
    for section in config.sections():
        result[section] = dict(config.items(section))
    
    return result


def load_env(filepath: str) -> Dict[str, str]:
    """Load an ENV file."""
    return dict(dotenv_values(filepath))


def load_txt(filepath: str) -> str:
    """Load a text file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def save_file(filepath: str, data: Any) -> None:
    """
    Save data to a file based on its extension.
    
    Args:
        filepath: Path to the file to save
        data: Data to save
    
    Raises:
        ValueError: If file format is not supported
    """
    path = Path(filepath)
    extension = path.suffix.lower()
    
    if extension == '.json':
        save_json(filepath, data)
    elif extension in ['.yaml', '.yml']:
        save_yaml(filepath, data)
    elif extension == '.ini':
        save_ini(filepath, data)
    elif extension == '.env':
        save_env(filepath, data)
    elif extension == '.txt':
        save_txt(filepath, data)
    else:
        raise ValueError(f"Unsupported file format: {extension}")


def save_json(filepath: str, data: Dict[str, Any]) -> None:
    """Save data to a JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_yaml(filepath: str, data: Any) -> None:
    """Save data to a YAML file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


def save_ini(filepath: str, data: Dict[str, Dict[str, str]]) -> None:
    """Save data to an INI file."""
    config = configparser.ConfigParser()
    
    for section, values in data.items():
        config.add_section(section)
        for key, value in values.items():
            config.set(section, key, str(value))
    
    with open(filepath, 'w', encoding='utf-8') as f:
        config.write(f)


def save_env(filepath: str, data: Dict[str, str]) -> None:
    """Save data to an ENV file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for key, value in data.items():
            f.write(f"{key}={value}\n")


def save_txt(filepath: str, data: str) -> None:
    """Save data to a text file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(data)
