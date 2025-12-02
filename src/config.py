"""
Configuration management for PM Component Query System
Uses Pydantic Settings for environment-based configuration
"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Required settings
    openai_api_key: str
    repo_path: Path

    # Cache configuration
    cache_dir: Path = Path.home() / ".cbagent" / "cache"
    cache_enabled: bool = True
    cache_ttl_days: int = 7
    cache_auto_invalidate: bool = True

    # Codex configuration
    codex_timeout: int = 300

    # Agent configuration
    technical_agent_model: str = "gpt-5-nano"
    translator_agent_model: str = "gpt-5-nano"

    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = None

    # Session configuration
    mcp_session_timeout: int = 360000
    max_retries: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    def validate_repo_path(self) -> None:
        """Validate that the repository path exists and is a git repository"""
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {self.repo_path}")

        if not self.repo_path.is_dir():
            raise ValueError(f"Repository path is not a directory: {self.repo_path}")

        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            raise ValueError(f"Repository path is not a git repository: {self.repo_path}")


# Global config instance
config: Optional[Settings] = None


def get_config() -> Settings:
    """Get or create the global configuration instance"""
    global config
    if config is None:
        config = Settings()
        config.validate_repo_path()
    return config


def reset_config() -> None:
    """Reset the global configuration (useful for testing)"""
    global config
    config = None
