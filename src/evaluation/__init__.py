"""
Evaluation system for CB Agent
Evaluates system outputs against ground truth using LLM-as-judge
"""

from src.evaluation.config import get_eval_config, reset_eval_config
from src.evaluation.loader import TestCaseLoader
from src.evaluation.runner import EvaluationRunner
from src.evaluation.models import (
    TestCase,
    TestSuite,
    GroundTruth,
    AnswerFormats,
    IdeaCoverageResult,
    AnswerEvaluation,
    TestCaseResult,
    EvaluationReport
)

__all__ = [
    "get_eval_config",
    "reset_eval_config",
    "TestCaseLoader",
    "EvaluationRunner",
    "TestCase",
    "TestSuite",
    "GroundTruth",
    "AnswerFormats",
    "IdeaCoverageResult",
    "AnswerEvaluation",
    "TestCaseResult",
    "EvaluationReport"
]
