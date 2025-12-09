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

    # Codex configuration
    codex_timeout: int = 600  # Increased to 10 minutes for complex queries

    # Agent configuration
    translator_agent_model: str = "gpt-5-nano"

    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = None

    # Session configuration
    max_retries: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    def validate_repo_path(self) -> None:
        """Validate that the repository path exists and is either a git repository or contains git repositories"""
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {self.repo_path}")

        if not self.repo_path.is_dir():
            raise ValueError(f"Repository path is not a directory: {self.repo_path}")

        # Check if the path itself is a git repository
        git_dir = self.repo_path / ".git"
        if git_dir.exists():
            return  # Valid: path is a git repository

        has_git_repos = any(
            (item / ".git").exists()
            for item in self.repo_path.iterdir()
            if item.is_dir()
        )

        if not has_git_repos:
            raise ValueError(
                f"Repository path is not a git repository and contains no git repositories: {self.repo_path}"
            )


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
