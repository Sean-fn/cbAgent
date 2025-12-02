"""
Technical Agent - Analyzes Git repositories for component information
Uses Codex/Claude to perform technical code analysis
"""

from pathlib import Path
from typing import Dict, Any
from openai import AsyncOpenAI


class TechnicalAgent:
    """
    Technical analysis agent that uses OpenAI to analyze code repositories

    This agent:
    - Searches for component definitions and usage examples
    - Identifies dependencies, imports, and related code
    - Extracts technical details like parameters, props, methods
    """

    def __init__(self, api_key: str, model: str = "gpt-5-nano", repo_path: Path = None):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.repo_path = repo_path

    async def analyze_component(
        self,
        component_name: str,
        query_type: str,
        context: str = ""
    ) -> str:
        """
        Analyze a component in the repository

        Args:
            component_name: Name of the component to analyze
            query_type: Type of analysis (usage, restrictions, dependencies, business_rules)
            context: Additional context or specific files to analyze

        Returns:
            Technical analysis of the component
        """
        prompt = self._build_prompt(component_name, query_type, context)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
            )

            return response.choices[0].message.content

        except Exception as e:
            raise RuntimeError(f"Technical analysis failed: {str(e)}")

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the technical agent"""
        return """You are a technical code analyst with expertise in analyzing codebases.

Your job:
1. Analyze code repositories for component information
2. Find usage examples, restrictions, dependencies, and business rules
3. Provide comprehensive technical details including:
   - File paths where components are defined
   - Import statements and module structure
   - Parameters, props, or configuration options
   - Code examples from the repository
   - Dependencies and related components
   - Technical constraints and limitations

Be thorough and precise in your analysis. Include specific file paths, line numbers when relevant, and actual code snippets."""

    def _build_prompt(self, component_name: str, query_type: str, context: str) -> str:
        """Build the analysis prompt based on query type"""
        base_prompts = {
            "usage": f"""Analyze the {component_name} component in the repository.

Find and provide:
1. Where {component_name} is defined (file paths)
2. How it's imported and used in other files
3. Parameters, props, or configuration it accepts
4. Actual code examples showing usage
5. Common usage patterns

{context}""",

            "restrictions": f"""Analyze restrictions and constraints for {component_name}.

Find and provide:
1. Input validation rules (type checking, prop validation, etc.)
2. Documented limitations in comments or documentation
3. Error handling and edge cases
4. What this component CANNOT do or handle
5. Technical constraints (browser support, dependencies, etc.)

{context}""",

            "dependencies": f"""Analyze dependencies for {component_name}.

Find and provide:
1. All import statements in the component file
2. External packages required (from package.json or similar)
3. Internal dependencies (other components it uses)
4. Required peer dependencies
5. Optional dependencies

{context}""",

            "business_rules": f"""Analyze business logic and rules in {component_name}.

Find and provide:
1. Validation logic that enforces business rules
2. Workflow steps or state transitions
3. Business constraints in comments or code
4. Conditional logic based on business requirements
5. Data transformation rules

{context}"""
        }

        return base_prompts.get(query_type, f"Analyze {component_name} component.\n\n{context}")


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
