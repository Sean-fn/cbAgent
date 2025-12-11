"""
Base judge protocol for evaluation system
Defines interface that all judges must implement
"""

from abc import ABC, abstractmethod
from src.evaluation.models import GroundTruth, IdeaCoverageResult


class BaseJudge(ABC):
    """Abstract base class for all judges"""

    @abstractmethod
    async def evaluate(
        self,
        answer: str,
        ground_truth: GroundTruth,
        question: str
    ) -> IdeaCoverageResult:
        """
        Evaluate an answer against ground truth

        Args:
            answer: The answer to evaluate (brief/detailed/raw)
            ground_truth: Ground truth containing key ideas
            question: Original question (for context)

        Returns:
            IdeaCoverageResult with coverage metrics
        """
        pass
