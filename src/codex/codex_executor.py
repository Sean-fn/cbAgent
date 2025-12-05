"""
Codex CLI Executor
Manages execution of OpenAI Codex CLI commands for code analysis
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


# Error Classes
class CodexExecutorError(Exception):
    """Base exception for Codex execution errors"""
    pass


class CodexTimeoutError(CodexExecutorError):
    """Codex execution timed out"""
    pass


class CodexAuthError(CodexExecutorError):
    """Codex CLI authentication failed"""
    pass


class CodexParseError(CodexExecutorError):
    """Failed to parse Codex JSON output"""
    pass


# Response Model
# NOTE: This class is currently unused but kept for backward compatibility
# The executor now returns plain strings directly from .msg.message
class CodexResponse:
    """Structured response from Codex CLI (DEPRECATED - not currently used)"""

    def __init__(
        self,
        analysis: str,
        files_analyzed: List[str],
        key_findings: List[str],
        code_examples: List[str],
        metadata: Optional[Dict] = None
    ):
        self.analysis = analysis
        self.files_analyzed = files_analyzed
        self.key_findings = key_findings
        self.code_examples = code_examples
        self.metadata = metadata or {}

    @classmethod
    def from_json(cls, data: dict) -> "CodexResponse":
        """Parse JSON output from Codex CLI"""
        try:
            return cls(
                analysis=data.get("analysis", ""),
                files_analyzed=data.get("files_analyzed", []),
                key_findings=data.get("key_findings", []),
                code_examples=data.get("code_examples", []),
                metadata=data.get("metadata", {})
            )
        except Exception as e:
            raise CodexParseError(f"Failed to parse Codex response: {str(e)}")

    def to_technical_output(self) -> str:
        """
        Convert to formatted technical output for TranslatorAgent

        This maintains compatibility with the existing pipeline by providing
        a formatted markdown-style output that the TranslatorAgent expects.
        """
        output_parts = []

        # Main analysis
        if self.analysis:
            output_parts.append(f"# Technical Analysis\n\n{self.analysis}")

        # Files analyzed
        if self.files_analyzed:
            output_parts.append("\n## Files Analyzed")
            for file_path in self.files_analyzed:
                output_parts.append(f"- {file_path}")

        # Key findings
        if self.key_findings:
            output_parts.append("\n## Key Findings")
            for finding in self.key_findings:
                output_parts.append(f"- {finding}")

        # Code examples
        if self.code_examples:
            output_parts.append("\n## Code Examples")
            for i, example in enumerate(self.code_examples, 1):
                output_parts.append(f"\n### Example {i}")
                output_parts.append(f"```\n{example}\n```")

        return "\n".join(output_parts)


# Main Executor Class
class CodexExecutor:
    """
    Executes Codex CLI commands for code analysis
    Uses `codex exec` with JSON output for structured responses
    """

    def __init__(self, repo_path: Path, timeout: int = 600, logs_dir: Optional[Path] = None):
        """
        Initialize CodexExecutor

        Args:
            repo_path: Path to the Git repository to analyze
            timeout: Timeout in seconds (default: 600 = 10 minutes)
            logs_dir: Directory to save raw Codex outputs (optional)

        Note: Authentication is handled by Codex CLI via 'codex login'
        """
        self.repo_path = Path(repo_path)
        self.timeout = timeout
        self.logs_dir = logs_dir or Path.home() / ".cbagent" / "codex_logs"

        # Create logs directory if it doesn't exist
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {self.repo_path}")

    async def execute_query(self, prompt: str) -> str:
        """
        Execute Codex CLI with query and return plain text response

        Args:
            prompt: The analysis query/task for Codex

        Returns:
            Plain text message from Codex (extracted from .msg.message)

        Raises:
            CodexTimeoutError: If query exceeds timeout
            CodexAuthError: If authentication fails
            CodexParseError: If .msg.message field not found
            CodexExecutorError: For other execution errors
        """
        # Run Codex CLI and get plain text message
        return await self._run_codex_cli(prompt)



    async def _run_codex_cli(self, task: str) -> str:
        """
        Run codex_script.sh with the task/question as argument and capture the returned value

        Args:
            task: The task/prompt for Codex

        Returns:
            Plain text message from the script (already extracted .msg.message by jq)

        Raises:
            CodexTimeoutError: If execution times out
            CodexAuthError: If authentication fails
            CodexExecutorError: For other execution errors
        """
        # Get the path to the script
        script_path = Path(__file__).parent / "codex_script.sh"

        if not script_path.exists():
            raise CodexExecutorError(f"Script not found: {script_path}")

        # Prepare the command - call the bash script with the task as argument
        cmd = [
            "bash",
            str(script_path),
            task
        ]

        try:
            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.repo_path)
            )

            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                # Kill the process if it times out
                process.kill()
                await process.wait()
                raise CodexTimeoutError(
                    f"Codex query timed out after {self.timeout} seconds. "
                    "Try a more specific query or increase CODEX_TIMEOUT."
                )

            # Get the output from the script
            output_text = stdout.decode().strip().replace("null\n", "")
            error_text = stderr.decode().strip() if stderr else ""

            # The script already extracts .msg.message using jq, so just return the output
            return output_text

        except FileNotFoundError:
            raise CodexExecutorError(
                "Bash or script not found. Please ensure bash is available and the script exists at: "
                f"{script_path}"
            )
        except Exception as e:
            if isinstance(e, (CodexTimeoutError, CodexAuthError, CodexExecutorError)):
                raise
            raise CodexExecutorError(f"Unexpected error running Codex script: {str(e)}")
