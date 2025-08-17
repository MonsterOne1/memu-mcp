"""Tests for configuration management"""

import json
import os
import tempfile
import pytest
from pathlib import Path

from memu_mcp_server.config import Config


class TestConfig:
    """Test configuration loading and validation"""
    
    def test_default_config(self):
        """Test default configuration values"""
        # Set required environment variable
        os.environ["MEMU_API_KEY"] = "test_key"
        
        try:
            config = Config()
            
            assert config.memu_api_key == "test_key"
            assert config.memu_base_url == "https://api.memu.so"
            assert config.server_name == "memu-mcp-server"
            assert config.server_version == "0.1.0"
            assert config.log_level == "INFO"
            assert config.default_user_id == "default_user"
            assert config.default_agent_id == "default_agent"
            assert config.max_conversation_length == 8000
            assert config.memory_retention_days == 30
            assert config.rate_limit_per_minute == 60
            assert config.rate_limit_per_hour == 1000
            assert config.allowed_origins == "*"
            assert config.api_timeout == 30
            
        finally:
            # Clean up
            if "MEMU_API_KEY" in os.environ:
                del os.environ["MEMU_API_KEY"]
    
    def test_config_from_env_vars(self):
        """Test configuration loading from environment variables"""
        env_vars = {
            "MEMU_API_KEY": "env_test_key",
            "MEMU_BASE_URL": "https://custom.api.url",
            "MCP_SERVER_NAME": "custom-server",
            "LOG_LEVEL": "DEBUG",
            "DEFAULT_USER_ID": "custom_user",
            "DEFAULT_AGENT_ID": "custom_agent",
            "MAX_CONVERSATION_LENGTH": "5000",
            "MEMORY_RETENTION_DAYS": "15",
            "RATE_LIMIT_PER_MINUTE": "30",
            "RATE_LIMIT_PER_HOUR": "500",
            "API_TIMEOUT": "60"
        }
        
        # Set environment variables
        for key, value in env_vars.items():
            os.environ[key] = value
        
        try:
            config = Config()
            
            assert config.memu_api_key == "env_test_key"
            assert config.memu_base_url == "https://custom.api.url"
            assert config.server_name == "custom-server"
            assert config.log_level == "DEBUG"
            assert config.default_user_id == "custom_user"
            assert config.default_agent_id == "custom_agent"
            assert config.max_conversation_length == 5000
            assert config.memory_retention_days == 15
            assert config.rate_limit_per_minute == 30
            assert config.rate_limit_per_hour == 500
            assert config.api_timeout == 60
            
        finally:
            # Clean up environment variables
            for key in env_vars:
                if key in os.environ:
                    del os.environ[key]
    
    def test_config_from_file(self):
        """Test configuration loading from JSON file"""
        config_data = {
            "memu_api_key": "file_test_key",
            "memu_base_url": "https://file.api.url",
            "server_name": "file-server",
            "log_level": "WARNING",
            "max_conversation_length": 12000,
            "api_timeout": 45
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name
        
        try:
            config = Config.from_file(config_file)
            
            assert config.memu_api_key == "file_test_key"
            assert config.memu_base_url == "https://file.api.url"
            assert config.server_name == "file-server"
            assert config.log_level == "WARNING"
            assert config.max_conversation_length == 12000
            assert config.api_timeout == 45
            
            # Check that defaults are still used for unspecified values
            assert config.default_user_id == "default_user"
            assert config.rate_limit_per_minute == 60
            
        finally:
            # Clean up temporary file
            Path(config_file).unlink()
    
    def test_config_file_not_found(self):
        """Test handling of missing configuration file"""
        with pytest.raises(FileNotFoundError):
            Config.from_file("nonexistent_config.json")
    
    def test_validate_required_fields(self):
        """Test validation of required configuration fields"""
        # Test with missing API key
        config = Config(
            memu_api_key="",  # Empty API key
            memu_base_url="https://api.memu.so"
        )
        
        with pytest.raises(ValueError, match="Required configuration field missing: memu_api_key"):
            config.validate_required_fields()
        
        # Test with valid API key
        config = Config(
            memu_api_key="valid_key",
            memu_base_url="https://api.memu.so"
        )
        
        assert config.validate_required_fields() is True
    
    def test_to_dict(self):
        """Test configuration conversion to dictionary"""
        os.environ["MEMU_API_KEY"] = "dict_test_key"
        
        try:
            config = Config()
            config_dict = config.to_dict()
            
            assert isinstance(config_dict, dict)
            assert config_dict["memu_api_key"] == "dict_test_key"
            assert config_dict["memu_base_url"] == "https://api.memu.so"
            assert config_dict["server_name"] == "memu-mcp-server"
            
        finally:
            if "MEMU_API_KEY" in os.environ:
                del os.environ["MEMU_API_KEY"]