# core/config/models.py
from pydantic import SecretStr
from pydantic_settings import BaseSettings

class LLMSettings(BaseSettings):
    """Settings for the LLM (Large Language Model) configuration."""
    OPENAI_API_KEY: SecretStr
    OPENAI_MODEL: str

class MCPSettings(BaseSettings):
    """Settings for the MCP (Model Context Protocol) configuration."""
    
    # TODO: Define the actual MCP dictionary settings
    
    DUMMY: SecretStr

class CombinedCoreSettings(LLMSettings, MCPSettings):
    """Combined settings for both LLM and MCP configurations."""
    pass