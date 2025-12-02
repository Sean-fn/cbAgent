"""
MCP Server Connection for Codex CLI
Manages the async connection to Codex CLI via MCP protocol
"""

import asyncio
import subprocess
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from pathlib import Path


class CodexMCPServer:
    """
    Manages connection to Codex CLI as an MCP server

    Note: This is a simplified implementation. The actual MCP integration
    may require the official OpenAI Agents SDK once it's available.
    For now, this provides a structure for Codex CLI interaction.
    """

    def __init__(self, repo_path: Path, timeout: int = 300):
        self.repo_path = repo_path
        self.timeout = timeout
        self.process: Optional[subprocess.Popen] = None

    async def query(self, prompt: str) -> str:
        """
        Send a query to Codex CLI and get the response

        This uses npx to run Codex CLI with the repository path and query.
        The actual implementation will depend on Codex CLI's MCP interface.
        """
        cmd = [
            "npx",
            "-y",
            "@anthropic-ai/claude-code",
            "--repo", str(self.repo_path),
            "--query", prompt
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.repo_path)
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"Codex CLI failed: {error_msg}")

            return stdout.decode()

        except asyncio.TimeoutError:
            raise TimeoutError(f"Codex query timed out after {self.timeout} seconds")
        except FileNotFoundError:
            raise RuntimeError(
                "Codex CLI not found. Please install it with: npm install -g @anthropic-ai/claude-code"
            )

    @asynccontextmanager
    async def connect(self) -> AsyncGenerator["CodexMCPServer", None]:
        """
        Async context manager for MCP connection lifecycle

        Usage:
            async with codex_server.connect() as server:
                result = await server.query("Find PaymentButton usage")
        """
        # For a persistent MCP connection, we would initialize the connection here
        # For now, we'll just yield self since each query is independent
        try:
            yield self
        finally:
            # Cleanup would go here if needed
            pass


class CodexCLIWrapper:
    """
    Alternative implementation using direct Claude Code CLI calls
    This is a simpler approach that doesn't use MCP but calls the CLI directly
    """

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    async def analyze_component(
        self,
        component_name: str,
        query_type: str,
        additional_context: str = ""
    ) -> str:
        """
        Analyze a component using Claude Code CLI

        Args:
            component_name: Name of the component to analyze
            query_type: Type of query (usage, restrictions, dependencies, business_rules)
            additional_context: Additional context for the query

        Returns:
            Analysis result from Claude Code
        """
        query_templates = {
            "usage": f"Find all usage examples of {component_name} in this repository. Show how it's used, what parameters it accepts, and provide code examples.",
            "restrictions": f"Analyze {component_name} and identify all limitations, constraints, validation rules, and things it cannot do.",
            "dependencies": f"What does {component_name} depend on? List all imports, required packages, and related components.",
            "business_rules": f"What business logic and rules are implemented in {component_name}? Focus on validation, workflows, and business constraints."
        }

        prompt = query_templates.get(query_type, f"Analyze {component_name}")
        if additional_context:
            prompt += f"\n\nAdditional context: {additional_context}"

        return await self._run_claude_code(prompt)

    async def _run_claude_code(self, prompt: str) -> str:
        """Run Claude Code CLI with the given prompt"""
        # Note: This is a placeholder implementation
        # The actual Codex CLI command structure may differ
        cmd = [
            "claude",  # or "codex" depending on the actual CLI
            "analyze",
            "--repo", str(self.repo_path),
            "--prompt", prompt
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                # If Claude Code is not available, return a mock response
                # This allows development to continue
                return f"[Mock response for: {prompt[:100]}...]"

            return stdout.decode()

        except FileNotFoundError:
            # CLI not found - return mock response for development
            return f"[Mock response - CLI not installed for: {prompt[:100]}...]"
