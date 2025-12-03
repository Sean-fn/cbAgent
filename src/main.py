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
from src.cache import CacheManager, CacheEntry
from src.agents.technical_agent import TechnicalAgent
from src.agents.translator_agent import TranslatorAgent
from git import Repo


console = Console()


class SessionState:
    """Tracks session state for progressive disclosure"""

    def __init__(self):
        self.last_query: Optional[str] = None
        self.last_detailed: Optional[str] = None


class PMQuerySystem:
    """Main application class for PM Component Query System"""

    def __init__(self):
        # Load configuration
        load_dotenv(override=True)
        self.config = get_config()

        # Initialize components
        self.cache = CacheManager(
            cache_dir=self.config.cache_dir,
            repo_path=self.config.repo_path,
            ttl_days=self.config.cache_ttl_days,
            auto_invalidate=self.config.cache_auto_invalidate
        ) if self.config.cache_enabled else None

        self.technical_agent = TechnicalAgent(
            api_key=None,  # Codex CLI uses session auth via 'codex login'
            model=None,    # Codex CLI determines model automatically
            repo_path=self.config.repo_path,
            logs_dir=self.config.codex_logs_dir
        )

        self.translator_agent = TranslatorAgent(
            api_key=self.config.openai_api_key,
            model=self.config.translator_agent_model
        )

        self.session_state = SessionState()

        # Get repository info
        self.repo = Repo(self.config.repo_path)
        self.current_commit = self.repo.head.commit.hexsha[:7]

    def show_welcome(self):
        """Display welcome banner"""
        welcome_text = f"""[bold cyan]PM Component Query System[/bold cyan]
Repository: {self.config.repo_path}
Status: Up to date (commit: {self.current_commit})

Type your question about any component, or try:
  • How do I use the PaymentButton?
  • What are the restrictions for UserProfile?
  • What does LoginForm depend on?
  • What are the business rules for CheckoutFlow?

Commands:
  • [bold]more[/bold] - Show detailed explanation for last query
  • [bold]status[/bold] - Show cache and repository status
  • [bold]cache clear[/bold] - Clear all cached results
  • [bold]help[/bold] - Show this help message
  • [bold]exit[/bold] or [bold]quit[/bold] - Exit the program
"""
        console.print(Panel(welcome_text, border_style="cyan"))

    async def process_query(self, user_input: str):
        """Process a user query by sending it directly to Codex"""
        console.print(f"\n[dim]Analyzing your query...[/dim]")

        # Check cache
        cached_entry: Optional[CacheEntry] = None
        if self.cache:
            cached_entry = self.cache.get(user_input)

        if cached_entry:
            brief = cached_entry.brief_output
            detailed = cached_entry.detailed_output
            console.print("[dim]✓ (cached result)[/dim]\n")
        else:
            # Perform analysis
            try:
                # Send query directly to Codex (no parsing!)
                technical_output = await self.technical_agent.analyze_query(user_input)

                # Translate to business language
                brief, detailed = await self.translator_agent.translate(
                    technical_output=technical_output,
                    component_name=""  # No component name needed anymore
                )

                # Cache the results
                if self.cache:
                    self.cache.set(
                        query=user_input,
                        brief_output=brief,
                        detailed_output=detailed
                    )

                console.print("[dim]✓[/dim]\n")

            except Exception as e:
                console.print(f"[red]❌ Error: {str(e)}[/red]")
                return

        # Display result
        self._display_result(user_input, brief, detailed)

        # Store for "more" command
        self.session_state.last_query = user_input
        self.session_state.last_detailed = detailed

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

    def show_status(self):
        """Show system status"""
        if self.cache:
            stats = self.cache.get_stats()
            cache_info = f"""Cache enabled: Yes
Cached queries: {stats['total_entries']}
Auto-invalidate: {'Enabled' if self.config.cache_auto_invalidate else 'Disabled'}
TTL: {self.config.cache_ttl_days} days"""
        else:
            cache_info = "Cache disabled"

        status_text = f"""[bold]Repository Status[/bold]
Path: {self.config.repo_path}
Current commit: {self.current_commit}

[bold]Cache Status[/bold]
{cache_info}

[bold]Agent Configuration[/bold]
Technical Agent: OpenAI Codex CLI (JSON mode)
Translator Agent: {self.config.translator_agent_model}
"""
        console.print(Panel(status_text, title="System Status", border_style="blue"))

    def clear_cache(self):
        """Clear cache"""
        if not self.cache:
            console.print("[yellow]Cache is disabled.[/yellow]")
            return

        count = self.cache.clear()
        console.print(f"[green]✓ Cleared {count} cached entries.[/green]")

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

                elif user_input.lower() == "status":
                    self.show_status()

                elif user_input.lower().startswith("cache clear"):
                    self.clear_cache()

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
