"""
JSON Reporter - Generates evaluation results as JSON + console summary
Saves results to file and displays rich console summary
"""

import json
from pathlib import Path
from rich.console import Console
from rich.table import Table

from src.evaluation.models import EvaluationReport
from src.evaluation.reporters.base import BaseReporter

console = Console()


class JsonReporter(BaseReporter):
    """Reports evaluation results as JSON + console summary"""

    def __init__(self, output_dir: Path):
        """
        Initialize JSON reporter

        Args:
            output_dir: Directory to save JSON reports
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate_report(self, report: EvaluationReport) -> Path:
        """
        Generate JSON report and console summary

        Args:
            report: EvaluationReport to save and display

        Returns:
            Path to saved JSON file
        """
        # Save JSON report
        timestamp = report.timestamp.strftime("%Y%m%d_%H%M%S")
        json_path = self.output_dir / f"{timestamp}_evaluation_results.json"

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(
                report.model_dump(mode='json'),
                f,
                indent=2,
                ensure_ascii=False,
                default=str  # Handle datetime serialization
            )

        # Print console summary
        self._print_summary(report)

        return json_path

    def _print_summary(self, report: EvaluationReport):
        """Print summary to console"""

        console.print("\n" + "="*80)
        console.print("[bold cyan]Evaluation Summary[/bold cyan]")
        console.print("="*80 + "\n")

        # Overview table
        overview = Table(title="Overview")
        overview.add_column("Metric", style="cyan")
        overview.add_column("Value", style="green")

        overview.add_row("Total Test Cases", str(report.total_test_cases))
        overview.add_row("Successful", str(report.successful))
        overview.add_row("Failed", str(report.failed))
        overview.add_row(
            "Success Rate",
            f"{(report.successful/report.total_test_cases)*100:.1f}%" if report.total_test_cases > 0 else "0.0%"
        )

        console.print(overview)
        console.print()

        # Coverage statistics
        if report.summary_stats:
            stats_table = Table(title="Idea Coverage Statistics")
            stats_table.add_column("Answer Type", style="cyan")
            stats_table.add_column("Avg Coverage", style="green")
            stats_table.add_column("Min Coverage", style="yellow")
            stats_table.add_column("Max Coverage", style="green")

            for answer_type in ["brief", "detailed", "raw"]:
                avg_key = f"{answer_type}_avg_coverage"
                if avg_key in report.summary_stats:
                    stats_table.add_row(
                        answer_type.capitalize(),
                        f"{report.summary_stats[avg_key]:.2%}",
                        f"{report.summary_stats[f'{answer_type}_min_coverage']:.2%}",
                        f"{report.summary_stats[f'{answer_type}_max_coverage']:.2%}"
                    )

            console.print(stats_table)
            console.print()

        # Performance
        if "avg_execution_time" in report.summary_stats:
            console.print(
                f"[cyan]Average Execution Time:[/cyan] "
                f"{report.summary_stats['avg_execution_time']:.2f}s"
            )

        # Failed test cases (if any)
        failed_tests = [r for r in report.results if r.error is not None]
        if failed_tests:
            console.print("\n[bold red]Failed Test Cases:[/bold red]")
            for result in failed_tests:
                console.print(f"  • [red]{result.test_case_id}[/red]: {result.error}")

        console.print("\n" + "="*80 + "\n")
