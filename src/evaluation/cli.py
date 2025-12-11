#!/usr/bin/env python3
"""
Evaluation CLI - Entry point for running evaluations
Orchestrates loading test cases, running evaluation, and generating reports
"""

import asyncio
from pathlib import Path
from rich.console import Console
from dotenv import load_dotenv

from src.config import get_config
from src.main import PMQuerySystem
from src.evaluation.config import get_eval_config
from src.evaluation.loader import TestCaseLoader
from src.evaluation.judges.idea_coverage_judge import IdeaCoverageJudge
from src.evaluation.runner import EvaluationRunner
from src.evaluation.reporters.json_reporter import JsonReporter

console = Console()


async def main():
    """Main entry point for evaluation CLI"""
    try:
        # Load environment variables
        load_dotenv(override=True)

        # Load configurations
        config = get_config()
        eval_config = get_eval_config()

        console.print("[bold cyan]Evaluation System[/bold cyan]\n")

        # Check if test cases file exists
        if not eval_config.test_cases_path.exists():
            console.print(f"[red]Error: Test cases file not found at {eval_config.test_cases_path}[/red]")
            console.print("\n[yellow]Please create a test cases file with the following format:[/yellow]")
            console.print("""
{
  "test_cases": [
    {
      "id": "001",
      "question": "How does PaymentButton work?",
      "ground_truth": {
        "key_ideas": [
          "Handles payment submission",
          "Validates card info",
          "Shows loading state"
        ]
      }
    }
  ]
}
            """)
            return

        # Load test cases
        console.print(f"[dim]Loading test cases from {eval_config.test_cases_path}...[/dim]")
        loader = TestCaseLoader()
        test_suite = await loader.load_from_file(eval_config.test_cases_path)
        console.print(f"[green]✓ Loaded {len(test_suite.test_cases)} test cases[/green]\n")

        # Create PM system
        console.print("[dim]Initializing PM Query System...[/dim]")
        pm_system = PMQuerySystem()
        console.print("[green]✓ PM Query System initialized[/green]\n")

        # Create judges
        console.print("[dim]Initializing judges...[/dim]")
        judges = [
            IdeaCoverageJudge(
                api_key=config.openai_api_key,
                model=eval_config.judge_model,
            )
        ]
        console.print(f"[green]✓ Initialized {len(judges)} judge(s)[/green]\n")

        # Run evaluation
        runner = EvaluationRunner(
            pm_system=pm_system,
            judges=judges,
            max_concurrent=eval_config.max_concurrent_evaluations
        )
        report = await runner.run_evaluation(test_suite.test_cases)

        # Generate report
        reporter = JsonReporter(output_dir=eval_config.results_output_dir)
        result_path = await reporter.generate_report(report)

        console.print(f"[green]✓ Results saved to: {result_path}[/green]\n")

    except ValueError as e:
        console.print(f"[red]Configuration Error:[/red] {str(e)}")
        console.print("\n[yellow]Please check your environment configuration:[/yellow]")
        console.print("1. Create a .env file based on env.template")
        console.print("2. Set OPENAI_API_KEY to your OpenAI API key")
        console.print("3. Set REPO_PATH to a valid Git repository path")
    except FileNotFoundError as e:
        console.print(f"[red]File Not Found:[/red] {str(e)}")
    except Exception as e:
        console.print(f"[red]Fatal Error:[/red] {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
