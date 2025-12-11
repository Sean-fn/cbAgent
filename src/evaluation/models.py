"""
Data models for evaluation system
Uses Pydantic for validation and type safety
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class GroundTruth(BaseModel):
    """Ground truth for a single test case"""
    key_ideas: List[str] = Field(
        description="List of key ideas that should appear in the answer"
    )


class TestCase(BaseModel):
    """Single evaluation test case"""
    id: str
    question: str
    ground_truth: GroundTruth


class TestSuite(BaseModel):
    """Collection of test cases"""
    test_cases: List[TestCase]


class AnswerFormats(BaseModel):
    """Three answer formats from the system"""
    brief: str
    detailed: str
    raw: str


class IdeaCoverageResult(BaseModel):
    """Result from idea coverage judge"""
    ideas_found: List[str]
    ideas_missing: List[str]
    coverage_score: float  # 0.0 to 1.0
    reasoning: str  # LLM's explanation


class AnswerEvaluation(BaseModel):
    """Evaluation for a single answer format"""
    answer_type: str  # "brief" | "detailed" | "raw"
    answer_text: str
    idea_coverage: IdeaCoverageResult


class TestCaseResult(BaseModel):
    """Result for a single test case"""
    test_case_id: str
    question: str
    ground_truth: GroundTruth
    answers: AnswerFormats
    evaluations: List[AnswerEvaluation]  # One per answer type
    execution_time: float
    error: Optional[str] = None


class EvaluationReport(BaseModel):
    """Complete evaluation report"""
    timestamp: datetime
    total_test_cases: int
    successful: int
    failed: int
    results: List[TestCaseResult]
    summary_stats: Dict[str, float]  # Overall metrics
