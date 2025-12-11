"""
Base reporter protocol for evaluation system
Defines interface that all reporters can implement
"""

from abc import ABC, abstractmethod
from pathlib import Path
from src.evaluation.models import EvaluationReport


class BaseReporter(ABC):
    """Abstract base class for all reporters"""

    @abstractmethod
    async def generate_report(self, report: EvaluationReport) -> Path:
        """
        Generate report from evaluation results

        Args:
            report: EvaluationReport with results

        Returns:
            Path to generated report file
        """
        pass
