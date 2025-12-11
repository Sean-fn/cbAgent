"""
Judges for evaluation system
Each judge implements a specific evaluation metric
"""

from src.evaluation.judges.base import BaseJudge
from src.evaluation.judges.idea_coverage_judge import IdeaCoverageJudge

__all__ = [
    "BaseJudge",
    "IdeaCoverageJudge"
]
