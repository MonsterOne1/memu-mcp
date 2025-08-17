"""Configuration management for memU MCP Server"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

from pydantic import BaseSettings, Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Configuration class for memU MCP Server"""
    
    # memU Configuration
    memu_api_key: str = Field(..., env="MEMU_API_KEY")
    memu_base_url: str = Field("https://api.memu.so", env="MEMU_BASE_URL")
    
    # Server Configuration
    server_name: str = Field("memu-mcp-server", env="MCP_SERVER_NAME")
    server_version: str = Field("0.1.0", env="MCP_SERVER_VERSION")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Memory Configuration
    default_user_id: str = Field("default_user", env="DEFAULT_USER_ID")
    default_agent_id: str = Field("default_agent", env="DEFAULT_AGENT_ID")
    max_conversation_length: int = Field(8000, env="MAX_CONVERSATION_LENGTH")
    memory_retention_days: int = Field(30, env="MEMORY_RETENTION_DAYS")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(1000, env="RATE_LIMIT_PER_HOUR")
    
    # Security
    allowed_origins: str = Field("*", env="ALLOWED_ORIGINS")
    api_timeout: int = Field(30, env="API_TIMEOUT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @classmethod
    def from_file(cls, config_path: Optional[str] = None) -> "Config":
        """Load configuration from JSON file"""
        if not config_path:
            return cls()
        
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        
        return cls(**config_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return self.dict()
    
    def validate_required_fields(self) -> bool:
        """Validate that required fields are set"""
        required_fields = ["memu_api_key"]
        
        for field in required_fields:
            if not getattr(self, field):
                raise ValueError(f"Required configuration field missing: {field}")
        
        return True