#!/usr/bin/env python3
"""
PM Component Query System
Interactive CLI for querying Git repositories for component information
"""

import asyncio
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from dotenv import load_dotenv

from src.config import get_config
from src.agents.technical_agent import TechnicalAgent
from src.agents.translator_agent import TranslatorAgent
from git import Repo


console = Console()


class SessionState:
    """Tracks session state for progressive disclosure"""

    def __init__(self):
        self.last_query: Optional[str] = None
        self.last_detailed: Optional[str] = None
        self.last_technical: Optional[str] = None


class PMQuerySystem:
    """Main application class for PM Component Query System"""

    def __init__(self):
        # Load configuration
        load_dotenv(override=True)
        self.config = get_config()

        # Initialize components
        self.technical_agent = TechnicalAgent(
            api_key=None,  # Codex CLI uses session auth via 'codex login'
            model=None,    # Codex CLI determines model automatically
            repo_path=self.config.repo_path
        )

        self.translator_agent = TranslatorAgent(
            api_key=self.config.openai_api_key,
            model=self.config.translator_agent_model
        )

        self.session_state = SessionState()

        # Get repository info (handle both single repos and directories with multiple repos)
        self.repo = None
        self.current_commit = None
        try:
            self.repo = Repo(self.config.repo_path)
            self.current_commit = self.repo.head.commit.hexsha[:7]
        except Exception:
            # Not a single git repo - might be a directory containing multiple repos
            pass

    def show_welcome(self):
        """Display welcome banner"""
        status_line = f"Status: Up to date (commit: {self.current_commit})" if self.current_commit else "Status: Multiple repositories"
        welcome_text = f"""[bold cyan]PM Component Query System[/bold cyan]
Repository: {self.config.repo_path}
{status_line}

Type your question about any component, or try:
  • How do I use the PaymentButton?
  • What are the restrictions for UserProfile?
  • What does LoginForm depend on?
  • What are the business rules for CheckoutFlow?

Commands:
  • [bold]more[/bold] - Show detailed explanation for last query
  • [bold]raw[/bold] - Show raw technical output from TechnicalAgent
  • [bold]status[/bold] - Show repository status
  • [bold]help[/bold] - Show this help message
  • [bold]exit[/bold] or [bold]quit[/bold] - Exit the program
"""
        console.print(Panel(welcome_text, border_style="cyan"))

    async def process_query(self, user_input: str):
        """Process a user query by sending it directly to Codex"""
        console.print(f"\n[dim]Analyzing your query...[/dim]")

        try:
            # Send query directly to Codex (no parsing!)
            technical_output = await self.technical_agent.analyze_query(user_input)

            # Translate to business language (parallel execution)
            brief_task = self.translator_agent._generate_brief(technical_output, user_input)
            detailed_task = self.translator_agent._generate_detailed(technical_output, user_input)

            # Wait for brief first and display immediately
            brief = await brief_task
            console.print("[dim]✓[/dim]\n")

            # Display brief immediately
            self._display_brief(user_input, brief)

            # Wait for detailed in background
            detailed = await detailed_task

        except Exception as e:
            console.print(f"[red]❌ Error: {str(e)}[/red]")
            return

        # Store for "more" and "raw" commands
        self.session_state.last_query = user_input
        self.session_state.last_detailed = detailed
        self.session_state.last_technical = technical_output

    def _display_brief(self, query: str, brief: str):
        """Display just the brief summary"""
        # Header
        console.print("━" * console.width)
        console.print(f"[bold]Query:[/bold] {query}")
        console.print("━" * console.width)

        # Brief summary
        console.print("\n[bold cyan]📄 Quick Summary[/bold cyan]\n")
        console.print(brief)

        # Prompt for more details
        console.print("\n" + "━" * console.width)
        console.print("[dim]💡 Want more details?[/dim]")
        console.print("[dim]   Type 'more' to see full explanation[/dim]")
        console.print("━" * console.width)
        console.print()

    def _display_result(self, query: str, brief: str, detailed: str):
        """Display query result with progressive disclosure"""
        # Header
        console.print("━" * console.width)
        console.print(f"[bold]Query:[/bold] {query}")
        console.print("━" * console.width)

        # Brief summary
        console.print("\n[bold cyan]📄 Quick Summary[/bold cyan]\n")
        console.print(brief)

        # Prompt for more details
        console.print("\n" + "━" * console.width)
        console.print("[dim]💡 Want more details?[/dim]")
        console.print("[dim]   Type 'more' to see full explanation[/dim]")
        console.print("━" * console.width)
        console.print()

    def show_more(self):
        """Show detailed explanation from last query"""
        if not self.session_state.last_detailed:
            console.print("[yellow]No previous query to show details for.[/yellow]")
            return

        console.print("\n[bold cyan]📋 Detailed Explanation[/bold cyan]\n")
        console.print(self.session_state.last_detailed)
        console.print("\n" + "━" * console.width + "\n")

    def show_raw(self):
        """Show raw technical output from TechnicalAgent"""
        if not self.session_state.last_technical:
            console.print("[yellow]No previous query to show raw output for.[/yellow]")
            return

        console.print("\n[bold cyan]🔧 Raw Technical Output[/bold cyan]\n")
        console.print(self.session_state.last_technical)
        console.print("\n" + "━" * console.width + "\n")

    def show_status(self):
        """Show system status"""
        commit_info = f"Current commit: {self.current_commit}" if self.current_commit else "Multiple repositories"
        status_text = f"""[bold]Repository Status[/bold]
Path: {self.config.repo_path}
{commit_info}

[bold]Agent Configuration[/bold]
Technical Agent: OpenAI Codex CLI (JSON mode)
Translator Agent: {self.config.translator_agent_model}
"""
        console.print(Panel(status_text, title="System Status", border_style="blue"))

    async def run(self):
        """Main interactive loop"""
        self.show_welcome()

        # Create prompt session with history
        session = PromptSession(history=InMemoryHistory())

        while True:
            try:
                # Get user input
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: session.prompt("\n❯ ")
                )

                user_input = user_input.strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() in ["exit", "quit", "q"]:
                    console.print("[cyan]Goodbye![/cyan]")
                    break

                elif user_input.lower() == "more":
                    self.show_more()

                elif user_input.lower() == "raw":
                    self.show_raw()

                elif user_input.lower() == "status":
                    self.show_status()

                elif user_input.lower() in ["help", "?"]:
                    self.show_welcome()

                else:
                    # Process as query
                    await self.process_query(user_input)

            except KeyboardInterrupt:
                console.print("\n[cyan]Use 'exit' to quit.[/cyan]")
            except EOFError:
                break
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")


async def main():
    """Entry point"""
    try:
        app = PMQuerySystem()
        await app.run()
    except ValueError as e:
        console.print(f"[red]Configuration Error:[/red] {str(e)}")
        console.print("\n[yellow]Please check your environment configuration:[/yellow]")
        console.print("1. Create a .env file based on env.template")
        console.print("2. Set OPENAI_API_KEY to your OpenAI API key")
        console.print("3. Set REPO_PATH to a valid Git repository path")
    except Exception as e:
        console.print(f"[red]Fatal Error:[/red] {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
