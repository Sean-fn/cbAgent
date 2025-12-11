#!/usr/bin/env python3
"""
Dataset Generator - Interactive script to create test cases
Extracts key ideas from answers using LLM
"""

import asyncio
import json
from pathlib import Path
from typing import List
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

console = Console()


class DatasetGenerator:
    """Generates test case datasets with LLM-assisted key idea extraction"""

    def __init__(self, api_key: str, model: str = "gpt-5-nano"):
        """
        Initialize dataset generator

        Args:
            api_key: OpenAI API key
            model: Model to use for key idea extraction
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.test_cases = []

    async def extract_key_ideas(self, question: str, answer: str) -> List[str]:
        """
        Extract key ideas from answer using LLM

        Args:
            question: The question being answered
            answer: The ground truth answer

        Returns:
            List of key ideas extracted from the answer
        """
        system_prompt = """You are a test case generator for an evaluation system.

Your task: Extract the key ideas from a given answer to a question.

Guidelines:
- Extract 3-7 key ideas that represent the main concepts in the answer
- Each idea should be a concise statement (5-15 words)
- Focus on the essential information, not minor details
- Ideas should be independently verifiable (can check if present/absent)
- Use business-friendly language, avoid overly technical jargon
- Each idea should represent a distinct concept

Return your extraction in JSON format:
{
  "key_ideas": [
    "First key idea here",
    "Second key idea here",
    "Third key idea here"
  ]
}"""

        user_prompt = f"""Question:
{question}

Answer:
{answer}

Extract the key ideas from this answer in the specified JSON format."""

        response = await self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        result = json.loads(response.choices[0].message.content)
        return result["key_ideas"]

    def add_test_case(self, test_id: str, question: str, key_ideas: List[str]):
        """
        Add a test case to the dataset

        Args:
            test_id: Unique test case ID
            question: The question
            key_ideas: List of key ideas (ground truth)
        """
        self.test_cases.append({
            "id": test_id,
            "question": question,
            "ground_truth": {
                "key_ideas": key_ideas
            }
        })

    def save_dataset(self, output_path: Path):
        """
        Save dataset to JSON file

        Args:
            output_path: Path to save JSON file
        """
        dataset = {"test_cases": self.test_cases}

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)

        console.print(f"\n[green]✓ Dataset saved to {output_path}[/green]")
        console.print(f"[dim]Total test cases: {len(self.test_cases)}[/dim]")

    def display_test_case(self, test_case: dict):
        """Display a test case in formatted panel"""
        content = f"""[bold cyan]ID:[/bold cyan] {test_case['id']}

[bold cyan]Question:[/bold cyan]
{test_case['question']}

[bold cyan]Key Ideas:[/bold cyan]"""

        for i, idea in enumerate(test_case['ground_truth']['key_ideas'], 1):
            content += f"\n  {i}. {idea}"

        console.print(Panel(content, border_style="cyan", title="Test Case"))


async def interactive_mode():
    """Run interactive dataset generation"""

    console.print(Panel.fit(
        "[bold cyan]Dataset Generator[/bold cyan]\n\n"
        "Generate test cases by providing questions and answers.\n"
        "The system will extract key ideas automatically using LLM.",
        border_style="cyan"
    ))

    # Load environment and get API key
    load_dotenv(override=True)
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        console.print("[red]Error: OPENAI_API_KEY not found in environment[/red]")
        console.print("Please set OPENAI_API_KEY in your .env file")
        return

    generator = DatasetGenerator(api_key=api_key)

    console.print("\n[bold]Instructions:[/bold]")
    console.print("1. Enter a question")
    console.print("2. Paste the ground truth answer (the ideal answer)")
    console.print("3. Review and edit the extracted key ideas")
    console.print("4. Repeat to add more test cases\n")

    test_counter = 1

    while True:
        console.print(f"\n[bold cyan]━━━ Test Case #{test_counter} ━━━[/bold cyan]\n")

        # Get question
        question = Prompt.ask("[cyan]Question[/cyan]")
        if not question.strip():
            console.print("[yellow]Skipping empty question[/yellow]")
            continue

        # Get answer
        console.print("\n[cyan]Ground Truth Answer[/cyan] (paste answer, then press Enter twice):")
        answer_lines = []
        empty_count = 0

        while empty_count < 1:
            try:
                line = input()
                if line.strip():
                    answer_lines.append(line)
                    empty_count = 0
                else:
                    empty_count += 1
            except EOFError:
                break

        answer = "\n".join(answer_lines).strip()

        if not answer:
            console.print("[yellow]Skipping empty answer[/yellow]")
            continue

        # Extract key ideas using LLM
        console.print("\n[dim]Extracting key ideas...[/dim]")

        try:
            key_ideas = await generator.extract_key_ideas(question, answer)

            console.print("\n[bold]Extracted Key Ideas:[/bold]")
            for i, idea in enumerate(key_ideas, 1):
                console.print(f"  {i}. {idea}")

            # Allow editing
            if Confirm.ask("\nEdit key ideas?", default=False):
                console.print("\n[dim]Enter key ideas one per line. Press Enter twice when done.[/dim]")
                key_ideas = []
                empty_count = 0

                while empty_count < 1:
                    idea = input(f"Idea {len(key_ideas) + 1}: ").strip()
                    if idea:
                        key_ideas.append(idea)
                        empty_count = 0
                    else:
                        empty_count += 1

            # Generate test ID
            test_id = f"{test_counter:03d}"

            # Add test case
            generator.add_test_case(test_id, question, key_ideas)

            # Display added test case
            console.print()
            generator.display_test_case(generator.test_cases[-1])

            test_counter += 1

            # Ask to continue
            if not Confirm.ask("\nAdd another test case?", default=True):
                break

        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            if not Confirm.ask("Continue anyway?", default=True):
                break

    # Save dataset
    if generator.test_cases:
        console.print("\n[bold]Saving dataset...[/bold]")

        output_path = Path("evaluation_data/test_cases.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if file exists
        if output_path.exists():
            if Confirm.ask(f"\n{output_path} already exists. Overwrite?", default=False):
                generator.save_dataset(output_path)
            else:
                # Save with timestamp
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = Path(f"evaluation_data/test_cases_{timestamp}.json")
                generator.save_dataset(output_path)
        else:
            generator.save_dataset(output_path)

        console.print("\n[green]✓ Dataset generation complete![/green]")
    else:
        console.print("\n[yellow]No test cases created.[/yellow]")


async def batch_mode(input_file: Path):
    """
    Generate dataset from batch input file

    Expected format (plain text):
    Q: Question here?
    A: Answer here...

    Q: Next question?
    A: Next answer...
    """
    console.print(f"[bold cyan]Batch Mode[/bold cyan]\n")
    console.print(f"Loading from: {input_file}\n")

    load_dotenv(override=True)
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        console.print("[red]Error: OPENAI_API_KEY not found[/red]")
        return

    generator = DatasetGenerator(api_key=api_key)

    # Parse input file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by question markers
    entries = []
    current_q = None
    current_a = []

    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('Q:'):
            if current_q and current_a:
                entries.append((current_q, '\n'.join(current_a)))
            current_q = line[2:].strip()
            current_a = []
        elif line.startswith('A:'):
            current_a.append(line[2:].strip())
        elif current_a:
            current_a.append(line)

    # Add last entry
    if current_q and current_a:
        entries.append((current_q, '\n'.join(current_a)))

    console.print(f"Found {len(entries)} question-answer pairs\n")

    # Process each entry
    for i, (question, answer) in enumerate(entries, 1):
        console.print(f"[dim]Processing {i}/{len(entries)}...[/dim]")

        try:
            key_ideas = await generator.extract_key_ideas(question, answer)
            test_id = f"{i:03d}"
            generator.add_test_case(test_id, question, key_ideas)
            console.print(f"[green]✓ Added test case {test_id}[/green]")
        except Exception as e:
            console.print(f"[red]✗ Failed: {str(e)}[/red]")

    # Save dataset
    output_path = Path("evaluation_data/test_cases.json")
    generator.save_dataset(output_path)


def main():
    """Main entry point"""
    import sys

    if len(sys.argv) > 1:
        # Batch mode
        input_file = Path(sys.argv[1])
        if not input_file.exists():
            console.print(f"[red]Error: File not found: {input_file}[/red]")
            return
        asyncio.run(batch_mode(input_file))
    else:
        # Interactive mode
        asyncio.run(interactive_mode())


if __name__ == "__main__":
    main()
