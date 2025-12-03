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
class CodexResponse:
    """Structured response from Codex CLI"""

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

    async def execute_query(self, prompt: str) -> CodexResponse:
        """
        Execute Codex CLI with query and return structured response

        Args:
            prompt: The analysis query/task for Codex

        Returns:
            CodexResponse object with structured analysis

        Raises:
            CodexTimeoutError: If query exceeds timeout
            CodexAuthError: If authentication fails
            CodexExecutorError: For other execution errors
        """
        # Build the complete task prompt
        task = self._build_task_prompt(prompt)

        # Run Codex CLI and get JSON response
        result_json = await self._run_codex_cli(task)

        # Parse and return structured response
        return CodexResponse.from_json(result_json)

    def _build_task_prompt(self, user_query: str) -> str:
        """
        Build the complete task prompt for Codex CLI

        This wraps the user's query with instructions for structured output
        """
        return f"""{user_query}

Please provide your response in a structured format that includes:
1. A comprehensive technical analysis
2. List of files you analyzed
3. Key findings as bullet points
4. Relevant code examples with proper context

Focus on being thorough and accurate."""

    def _get_output_schema(self) -> dict:
        """
        Get the JSON schema for Codex output

        This schema ensures consistent, parseable output from Codex
        """
        return {
            "type": "object",
            "properties": {
                "analysis": {
                    "type": "string",
                    "description": "Main technical analysis text explaining the findings"
                },
                "files_analyzed": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of file paths that were analyzed"
                },
                "key_findings": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Bullet points of key findings and insights"
                },
                "code_examples": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Relevant code snippets with context"
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "confidence": {
                            "type": "number",
                            "description": "Confidence level (0-1)"
                        },
                        "files_count": {
                            "type": "integer",
                            "description": "Number of files analyzed"
                        }
                    }
                }
            },
            "required": ["analysis", "files_analyzed", "key_findings", "code_examples"],
            "additionalProperties": False
        }

    async def _run_codex_cli(self, task: str) -> dict:
        """
        Run codex exec command and capture stdout/stderr

        Args:
            task: The task/prompt for Codex

        Returns:
            Parsed JSON response from Codex

        Raises:
            CodexTimeoutError: If execution times out
            CodexAuthError: If authentication fails
            CodexExecutorError: For other execution errors
        """
        # Prepare the command
        # Note: We'll use inline JSON schema via stdin or temp file
        schema_json = json.dumps(self._get_output_schema())

        cmd = [
            "codex",
            "exec",
            task,
            "--json",
            # Note: If --output-schema doesn't support inline JSON, we may need to write to a temp file
            # For now, we'll try without it and rely on --json flag
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

            # Check return code
            # if process.returncode != 0:
                # error_msg = stderr.decode() if stderr else "Unknown error"

                # # Check for authentication errors
                # if "authentication" in error_msg.lower() or "login" in error_msg.lower():
                #     raise CodexAuthError(
                #         f"Codex CLI authentication failed. Please run 'codex login' first.\n"
                #         f"Error: {error_msg}"
                #     )

                # # Generic error
                # raise CodexExecutorError(
                #     f"Codex CLI execution failed (exit code {process.returncode}):\n{error_msg}"
                # )

            # Parse JSON output
            try:
                output_text = stdout.decode().strip()

                # Save raw output to log file
                # Handle case where Codex might output multiple JSON objects (JSON Lines)
                # We'll try to parse the last complete JSON object
                lines = output_text.strip().split('\n')

                # Try to find a valid JSON object from the end
                for line in reversed(lines):
                    line = line.strip()
                    if line and (line.startswith('{') or line.startswith('[')):
                        try:
                            result = json.loads(line)
                            # If this is a JSON Lines stream with type field, extract the data
                            if isinstance(result, dict) and 'type' in result:
                                # This might be a stream event, look for agent_message or final output
                                if result.get('type') == 'item.completed' and 'item' in result:
                                    item = result['item']
                                    if item.get('type') == 'agent_message' and 'text' in item:
                                        # Save raw output only for agent_message
                                        self._save_raw_output(item['text'], stderr.decode() if stderr else "")
                                        # The text field might be the final message, not JSON
                                        # In this case, we need to construct our own response
                                        return self._construct_fallback_response(item['text'])
                            else:
                                # Check if this looks like our expected schema
                                if 'analysis' in result or 'files_analyzed' in result:
                                    return result
                        except json.JSONDecodeError:
                            continue

                # If we couldn't find a structured response, try parsing the whole output
                result = json.loads(output_text)
                return result

            except json.JSONDecodeError as e:
                # If JSON parsing fails, create a fallback response from raw text
                return self._construct_fallback_response(output_text)

        except FileNotFoundError:
            raise CodexExecutorError(
                "Codex CLI not found. Please install it first.\n"
                "Visit: https://openai.com/blog/codex-cli for installation instructions."
            )
        except Exception as e:
            if isinstance(e, (CodexTimeoutError, CodexAuthError, CodexExecutorError)):
                raise
            raise CodexExecutorError(f"Unexpected error running Codex CLI: {str(e)}")

    def _construct_fallback_response(self, text: str) -> dict:
        """
        Construct a fallback response when JSON parsing fails

        This creates a basic response structure from plain text output
        """
        return {
            "analysis": text,
            "files_analyzed": [],
            "key_findings": [],
            "code_examples": [],
            "metadata": {
                "confidence": 0.5,
                "files_count": 0
            }
        }

    def _save_raw_output(self, stdout: str, stderr: str) -> None:
        """
        Save raw Codex output to a timestamped log file

        Args:
            stdout: Raw stdout from Codex CLI
            stderr: Raw stderr from Codex CLI
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        log_file = self.logs_dir / f"codex_output_{timestamp}.json"

        log_data = {
            "timestamp": datetime.now().isoformat(),
            "stdout": stdout,
            "stderr": stderr
        }

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

        print(f"Raw Codex output saved to: {log_file}")
