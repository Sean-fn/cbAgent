"""
Configuration management for evaluation system
Uses Pydantic Settings for environment-based configuration
"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class EvaluationSettings(BaseSettings):
    """Evaluation-specific settings loaded from environment variables"""

    # Judge configuration
    judge_model: str = "gpt-5-nano"

    # Test data paths
    test_cases_path: Path = Path("evaluation_data/test_cases.json")
    results_output_dir: Path = Path("evaluation_results")

    # Execution settings
    max_concurrent_evaluations: int = 1  # Run 3 tests in parallel
    evaluation_timeout: int = 900  # 15 minutes per test

    model_config = SettingsConfigDict(
        env_prefix="EVAL_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global config instance
eval_config: Optional[EvaluationSettings] = None


def get_eval_config() -> EvaluationSettings:
    """Get or create the global evaluation configuration instance"""
    global eval_config
    if eval_config is None:
        eval_config = EvaluationSettings()
    return eval_config


def reset_eval_config() -> None:
    """Reset the global evaluation configuration (useful for testing)"""
    global eval_config
    eval_config = None
