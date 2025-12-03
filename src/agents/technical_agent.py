"""
Technical Agent - Analyzes Git repositories for component information
Uses Codex CLI directly (no regex parsing - passes queries directly to Codex)
"""

from pathlib import Path
from typing import Optional
from src.codex.codex_executor import CodexExecutor, CodexResponse, CodexTimeoutError, CodexAuthError


class TechnicalAgent:
    """
    Technical analysis agent that uses Codex CLI to analyze code repositories

    This agent:
    - Passes user queries directly to Codex without parsing
    - Lets Codex handle component identification and analysis
    - Returns raw technical analysis from Codex
    """

    def __init__(self, api_key: str = None, model: str = None, repo_path: Path = None, logs_dir: Optional[Path] = None):
        """
        Initialize the TechnicalAgent with Codex CLI executor

        Args:
            api_key: Deprecated - Codex CLI uses session-based auth via 'codex login'
            model: Deprecated - Codex CLI determines model automatically
            repo_path: Path to the repository to analyze
            logs_dir: Directory to save raw Codex outputs (optional)
        """
        self.repo_path = repo_path
        self.codex = CodexExecutor(repo_path=repo_path, timeout=600, logs_dir=logs_dir)

    async def analyze_query(self, user_query: str) -> str:
        """
        Analyze a user query directly using Codex

        Args:
            user_query: Raw user query (e.g., "How do I use the PaymentButton?")

        Returns:
            Technical analysis from Codex formatted as markdown text
        """
        # Build the prompt for Codex
        prompt = self._build_codex_prompt(user_query)

        try:
            # Send query to Codex and get structured response
            response: CodexResponse = await self.codex.execute_query(prompt)

            # Convert to formatted text for TranslatorAgent
            return response.to_technical_output()

        except CodexTimeoutError as e:
            raise RuntimeError(f"Analysis timed out: {str(e)}")
        except CodexAuthError as e:
            raise RuntimeError(f"Codex authentication failed: {str(e)}. Please run 'codex login'.")
        except Exception as e:
            raise RuntimeError(f"Codex analysis failed: {str(e)}")

    def _build_codex_prompt(self, user_query: str) -> str:
        """
        Build the prompt for Codex based on the user's query

        Args:
            user_query: The raw user question

        Returns:
            Formatted prompt for Codex
        """
        return f"""Analyze this codebase to answer the following question:

{user_query}

Provide a comprehensive technical analysis including:
- Relevant file paths and code locations
- Code examples and usage patterns
- Dependencies and imports
- Technical constraints and limitations
- Implementation details

Focus on being thorough and accurate. Include actual code snippets from the repository."""


class MockTechnicalAgent:
    """Mock agent for testing when OpenAI API is not available"""

    async def analyze_component(
        self,
        component_name: str,
        query_type: str,
        context: str = ""
    ) -> str:
        """Return mock technical analysis"""
        return f"""Technical Analysis of {component_name} ({query_type}):

File: src/components/{component_name}.tsx

Imports:
import React from 'react';
import {{ useState }} from 'react';

Definition:
export const {component_name} = (props) => {{
  const {{ amount, onSuccess, onError }} = props;
  // Implementation details...
  return <button>Process Payment</button>;
}}

Usage Example:
import {{ {component_name} }} from '@/components/{component_name}';

<{component_name}
  amount={{99.99}}
  onSuccess={{handleSuccess}}
  onError={{handleError}}
/>

Dependencies:
- react (peer dependency)
- Internal: PaymentProcessor, ValidationUtils

This is mock data for development purposes."""
