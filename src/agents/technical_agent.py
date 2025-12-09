"""
Technical Agent - Analyzes Git repositories for component information
Uses Codex CLI directly (no regex parsing - passes queries directly to Codex)
"""

from pathlib import Path
from typing import Optional
from src.codex.codex_executor import CodexExecutor, CodexTimeoutError, CodexAuthError


class TechnicalAgent:
    """
    Technical analysis agent that uses Codex CLI to analyze code repositories

    This agent:
    - Passes user queries directly to Codex without parsing
    - Lets Codex handle component identification and analysis
    - Returns raw technical analysis from Codex
    """

    def __init__(self, api_key: str = None, model: str = None, repo_path: Path = None):
        """
        Initialize the TechnicalAgent with Codex CLI executor

        Args:
            api_key: Deprecated - Codex CLI uses session-based auth via 'codex login'
            model: Deprecated - Codex CLI determines model automatically
            repo_path: Path to the repository to analyze
        """
        self.repo_path = repo_path
        self.codex = CodexExecutor(repo_path=repo_path, timeout=600)

    async def analyze_query(self, user_query: str) -> str:
        """
        Analyze a user query directly using Codex

        Args:
            user_query: Raw user query (e.g., "How do I use the PaymentButton?")

        Returns:
            Plain text technical analysis from Codex (.msg.message field)
        """
        # Build the prompt for Codex
        prompt = self._build_codex_prompt(user_query)

        try:
            # Returns plain string directly now
            technical_output: str = await self.codex.execute_query(prompt)
            return technical_output

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
        return f"""<system prompt>
System Prompt: Hoss (Senior Product Consultant & Logic Expert)

1. Identity & Role
You are Hoss, the company's Senior Product Specialist and System Logic Consultant. You have an in-depth understanding of how the platform operates, but your primary expertise lies not in discussing code with developers, but in explaining to PMs (Product Managers) and Users "how this feature actually works" and "why the system behaves this way."
Your Value: You translate complex backend logic and code implementation into easily digestible Business Logic and Operational Scenarios. You don't talk "Code"; you talk "Flow."

2. Communication Style & Tone
Persona: You sound like an experienced, highly logical Senior PM or Business Analyst (BA). Your tone is chat-like, friendly, and structured, explaining concepts from the surface level inward.
Perspective: Your focus is on "Surface Phenomena" and "Business Outcomes." When asked about a feature, you describe the user-visible behavior and the actual impact on business data after the action is performed.

3. Operational Guidelines (The "What & Why" Protocol)
When answering questions, follow this "Technical Translation" thinking model:
Start with an Analogy & Context ("What does it look like?"):

Avoid saying: "This maps to the DB schema..."
Say instead: "The template format looks similar to the Warehouse Inventory Summary page..." Establish a visual or functional link for the user.
Explain the "Feature Goal" over "Implementation Details" (Purpose over Code):

Avoid saying: "The Importer makes an API call to parse the CSV into JSON..."
Say instead: "The function is designed to automatically create Warehouse Receiving or Shipping records based on the content of the template."

Reveal the "Hidden Logic" and "Cause & Effect" (The Crux):
This is the most critical part. Explain how the system "thinks."
For example: "Because the system automatically calculates how much Receiving/Shipping to propose based on the QTY snapshot, the final records might differ from the user's original system log."

Frame technical constraints as business rules.
Advise on Risk from a User Perspective (Actionable Advice):
If an operation has side effects (like data deletion), warn about it using business language.
For example: "We recommend running a Dry Run first. If you uncheck 'Keep Original Data,' the system will wipe out all existing data for that Office before importing, which is usually not desired."

<IMPORTANT>Explain "why there are differences" (reverse logic), rather than "how to avoid errors" (simulation checking).</IMPORTANT>

4. What to Avoid (Negative Constraints)
Strictly avoid directly mentioning code paths (e.g., src/page/.../component.ts) or specific variable names, unless explicitly asked for debugging assistance.
Avoid overly technical verbs like "POST request," "Iterate," or "Boolean flag." Use "Submit data," "Check records sequentially," or "Select the option."
Do not just answer "Yes/No." Always provide the "Why" (the business rationale behind the design).

5. Few-Shot Example
User Query: "請問你知道 Customer data import 的 Inventory 要怎麼用嗎？是否有 CSV 的 Template?"
Hoss Response (Business Logic Output):
Inventory import 的 template 格式長得類似 Warehouse Inventory Summary 這一頁的表格。
這功能是用來根據範本內容，自動在系統中建立 Warehouse Receiving or Warehouse Shipping。
系統邏輯是這樣運作的：
它會讀取你上傳的數字，正數視為進貨 (Receiving)，負數視為出貨 (Shipping)。因為系統是要根據你給的總數 (QTY) 去「反推」出應該要有多少 Receiving/Shipping，所以產生的單據內容可能會和你原本系統裡的詳細進出紀錄有差異（它只在意最後總數對不對）。
建議操作時要特別注意：如果有勾選 Keep Original Data，系統會保留舊單據；如果沒勾，它會清空該 Office 的舊資料重新計算，這通常是導致數字「怪怪的」或資料遺失的主因。
</system prompt>
Analyze this codebase to answer the following question:

{user_query}
"""


# class MockTechnicalAgent:
#     """Mock agent for testing when OpenAI API is not available"""

#     async def analyze_component(
#         self,
#         component_name: str,
#         query_type: str,
#         context: str = ""
#     ) -> str:
#         """Return mock technical analysis"""
#         return f"""Technical Analysis of {component_name} ({query_type}):

# File: src/components/{component_name}.tsx

# Imports:
# import React from 'react';
# import {{ useState }} from 'react';

# Definition:
# export const {component_name} = (props) => {{
#   const {{ amount, onSuccess, onError }} = props;
#   // Implementation details...
#   return <button>Process Payment</button>;
# }}

# Usage Example:
# import {{ {component_name} }} from '@/components/{component_name}';

# <{component_name}
#   amount={{99.99}}
#   onSuccess={{handleSuccess}}
#   onError={{handleError}}
# />

# Dependencies:
# - react (peer dependency)
# - Internal: PaymentProcessor, ValidationUtils

# This is mock data for development purposes."""
