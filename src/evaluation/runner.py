"""
Evaluation Runner - Orchestrates evaluation pipeline
Runs test cases through PM system and evaluates results
"""

import asyncio
from datetime import datetime
from typing import List
from rich.console import Console
from rich.progress import Progress

from src.main import PMQuerySystem
from src.evaluation.models import (
    TestCase, TestCaseResult, EvaluationReport,
    AnswerFormats, AnswerEvaluation
)
from src.evaluation.judges.base import BaseJudge

console = Console()


class EvaluationRunner:
    """Runs evaluation pipeline on test cases"""

    def __init__(
        self,
        pm_system: PMQuerySystem,
        judges: List[BaseJudge],
        max_concurrent: int = 3
    ):
        """
        Initialize evaluation runner

        Args:
            pm_system: PMQuerySystem instance for running queries
            judges: List of judges to evaluate answers
            max_concurrent: Maximum concurrent test evaluations (default: 3)
        """
        self.pm_system = pm_system
        self.judges = judges
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def run_evaluation(
        self,
        test_cases: List[TestCase]
    ) -> EvaluationReport:
        """
        Run evaluation on all test cases

        Args:
            test_cases: List of test cases to evaluate

        Returns:
            EvaluationReport with complete results
        """
        console.print(f"\n[bold cyan]Starting Evaluation[/bold cyan]")
        console.print(f"Total test cases: {len(test_cases)}")
        console.print(f"Concurrent executions: {self.max_concurrent}\n")

        start_time = datetime.now()

        # Run test cases with concurrency limit
        tasks = [
            self._evaluate_test_case(tc)
            for tc in test_cases
        ]

        with Progress() as progress:
            task = progress.add_task(
                "[cyan]Evaluating...",
                total=len(test_cases)
            )

            results = []
            for coro in asyncio.as_completed(tasks):
                result = await coro
                results.append(result)
                progress.update(task, advance=1)

        # Calculate summary statistics
        successful = sum(1 for r in results if r.error is None)
        failed = len(results) - successful

        summary_stats = self._calculate_summary_stats(results)

        return EvaluationReport(
            timestamp=start_time,
            total_test_cases=len(test_cases),
            successful=successful,
            failed=failed,
            results=results,
            summary_stats=summary_stats
        )

    async def _evaluate_test_case(
        self,
        test_case: TestCase
    ) -> TestCaseResult:
        """
        Evaluate a single test case

        Args:
            test_case: Test case to evaluate

        Returns:
            TestCaseResult with evaluation results
        """
        async with self.semaphore:
            start_time = datetime.now()

            try:
                # Get all three answer formats from PM system
                answers = await self._get_answers(test_case.question)

                # Evaluate each answer format with all judges
                evaluations = []
                for answer_type, answer_text in [
                    ("brief", answers.brief),
                    ("detailed", answers.detailed),
                    ("raw", answers.raw)
                ]:
                    # Run all judges on this answer
                    judge_results = await asyncio.gather(*[
                        judge.evaluate(
                            answer=answer_text,
                            ground_truth=test_case.ground_truth,
                            question=test_case.question
                        )
                        for judge in self.judges
                    ])

                    # We currently only have one judge (idea coverage)
                    idea_coverage = judge_results[0]

                    evaluations.append(AnswerEvaluation(
                        answer_type=answer_type,
                        answer_text=answer_text,
                        idea_coverage=idea_coverage
                    ))

                execution_time = (datetime.now() - start_time).total_seconds()

                return TestCaseResult(
                    test_case_id=test_case.id,
                    question=test_case.question,
                    ground_truth=test_case.ground_truth,
                    answers=answers,
                    evaluations=evaluations,
                    execution_time=execution_time,
                    error=None
                )

            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds()

                return TestCaseResult(
                    test_case_id=test_case.id,
                    question=test_case.question,
                    ground_truth=test_case.ground_truth,
                    answers=AnswerFormats(brief="", detailed="", raw=""),
                    evaluations=[],
                    execution_time=execution_time,
                    error=str(e)
                )

    async def _get_answers(self, question: str) -> AnswerFormats:
        """
        Get all three answer formats from PM system

        Args:
            question: Question to ask

        Returns:
            AnswerFormats with brief, detailed, and raw answers
        """
        # Get technical analysis (raw output)
        technical_output = await self.pm_system.technical_agent.analyze_query(question)

        # Get brief and detailed translations in parallel
        brief_task = self.pm_system.translator_agent._generate_brief(
            technical_output, question
        )
        detailed_task = self.pm_system.translator_agent._generate_detailed(
            technical_output, question
        )

        brief, detailed = await asyncio.gather(brief_task, detailed_task)

        return AnswerFormats(
            brief=brief,
            detailed=detailed,
            raw=technical_output
        )

    def _calculate_summary_stats(
        self,
        results: List[TestCaseResult]
    ) -> dict:
        """
        Calculate summary statistics across all results

        Args:
            results: List of test case results

        Returns:
            Dictionary with summary statistics
        """
        successful_results = [r for r in results if r.error is None]

        if not successful_results:
            return {}

        # Calculate average coverage by answer type
        stats = {}
        for answer_type in ["brief", "detailed", "raw"]:
            scores = [
                eval.idea_coverage.coverage_score
                for r in successful_results
                for eval in r.evaluations
                if eval.answer_type == answer_type
            ]

            if scores:
                stats[f"{answer_type}_avg_coverage"] = sum(scores) / len(scores)
                stats[f"{answer_type}_min_coverage"] = min(scores)
                stats[f"{answer_type}_max_coverage"] = max(scores)

        # Average execution time
        exec_times = [r.execution_time for r in successful_results]
        if exec_times:
            stats["avg_execution_time"] = sum(exec_times) / len(exec_times)

        return stats
