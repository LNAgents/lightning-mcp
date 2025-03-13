#!/usr/bin/env python
"""
Config utilities for Lightning MCP.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Default paths
DEFAULT_CONFIG_PATH = "config.json"
DEFAULT_CONFIG_ENV_VAR = "LIGHTNING_MCP_CONFIG"

def expand_path(path: str) -> str:
    """
    Expand a file path that may include ~ for home directory.
    
    Args:
        path: The path to expand
        
    Returns:
        The expanded path as a string
    """
    return os.path.expanduser(path)

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the config file, or None to use environment variable
                    or default path
    
    Returns:
        Dictionary containing configuration
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        json.JSONDecodeError: If the config file isn't valid JSON
    """
    # Determine config path
    if config_path is None:
        config_path = os.environ.get(DEFAULT_CONFIG_ENV_VAR, DEFAULT_CONFIG_PATH)
    
    # Expand path if needed
    config_path = expand_path(config_path)
    
    # Check if file exists
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    # Load and parse JSON
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    return config

def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate the configuration to ensure it has all required fields.
    
    Args:
        config: Configuration dictionary to validate
        
    Raises:
        ValueError: If configuration is missing required fields
    """
    # Check for required top-level sections
    required_sections = ["server", "lightning", "security", "payment_limits"]
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    # Check server section
    required_server_fields = ["host", "port"]
    for field in required_server_fields:
        if field not in config["server"]:
            raise ValueError(f"Missing required server configuration field: {field}")
    
    # Check lightning section
    if "implementation" not in config["lightning"]:
        raise ValueError("Missing required lightning configuration field: implementation")
    
    impl = config["lightning"]["implementation"]
    if impl not in ["lnd", "c-lightning", "eclair", "external"]:
        raise ValueError(f"Unsupported lightning implementation: {impl}")
    
    if "connection" not in config["lightning"]:
        raise ValueError("Missing required lightning configuration field: connection")
    
    if impl not in config["lightning"]["connection"]:
        raise ValueError(f"Missing connection configuration for implementation: {impl}")
    
    # Implementation-specific validation
    if impl == "lnd":
        required_lnd_fields = ["rpc_server", "tls_cert_path", "macaroon_path"]
        for field in required_lnd_fields:
            if field not in config["lightning"]["connection"]["lnd"]:
                raise ValueError(f"Missing required LND configuration field: {field}")

def get_config_with_validation(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load and validate configuration.
    
    Args:
        config_path: Path to the config file, or None to use environment variable
                    or default path
    
    Returns:
        Dictionary containing validated configuration
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        json.JSONDecodeError: If the config file isn't valid JSON
        ValueError: If configuration is missing required fields
    """
    config = load_config(config_path)
    validate_config(config)
    return config 