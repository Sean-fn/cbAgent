"""
Business Translator Agent - Converts technical output to PM-friendly language
Generates both brief and detailed versions for progressive disclosure
"""

from typing import Tuple
from openai import AsyncOpenAI


class TranslatorAgent:
    """
    Business translator agent that reformats technical analysis into
    clear, jargon-free explanations for Product Managers

    This agent:
    - Removes technical jargon, file paths, and code syntax
    - Focuses on business logic and practical usage
    - Explains WHAT the component does and WHY it matters
    - Generates two versions: brief (3-4 sentences) and detailed
    """

    def __init__(self, api_key: str, model: str = "gpt-5-nano"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def translate(self, technical_output: str, component_name: str) -> Tuple[str, str]:
        """
        Translate technical output to business-friendly language

        Args:
            technical_output: Technical analysis from TechnicalAgent
            component_name: Name of the component being analyzed

        Returns:
            Tuple of (brief_summary, detailed_explanation)
        """
        try:
            # Generate brief summary
            brief = await self._generate_brief(technical_output, component_name)

            # Generate detailed explanation
            detailed = await self._generate_detailed(technical_output, component_name)

            return brief, detailed

        except Exception as e:
            raise RuntimeError(f"Translation failed: {str(e)}")

    async def _generate_brief(self, technical_output: str, component_name: str) -> str:
        """Generate a brief 3-4 sentence summary"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": self._get_brief_system_prompt()
                },
                {
                    "role": "user",
                    "content": f"Component: {component_name}\n\nTechnical Analysis:\n{technical_output}"
                }
            ],
        )

        return response.choices[0].message.content.strip()

    async def _generate_detailed(self, technical_output: str, component_name: str) -> str:
        """Generate a detailed business-friendly explanation"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": self._get_detailed_system_prompt()
                },
                {
                    "role": "user",
                    "content": f"Component: {component_name}\n\nTechnical Analysis:\n{technical_output}"
                }
            ],
        )

        return response.choices[0].message.content.strip()

    def _get_brief_system_prompt(self) -> str:
        """System prompt for generating brief summaries"""
        return """You are a business communication expert who translates technical code analysis into clear summaries for Product Managers.

Your task: Create a brief 3-4 sentence summary that explains WHAT the component does and WHY it matters from a business perspective.

Rules:
- NO technical jargon (props, functions, imports, etc.)
- NO file paths or code syntax
- Focus on user-facing behavior and business value
- Use simple, conversational language
- Explain in terms a non-technical person would understand

Example:
TECHNICAL: "The PaymentButton component accepts an `amount` prop (type: number) and `onSuccess` callback..."
BRIEF: "The Payment Button allows customers to complete purchases by clicking to process their payment. It handles the payment amount and notifies the system when the transaction succeeds or fails. This component is used throughout the checkout process."

Now translate the following technical analysis into a brief business summary:"""

    def _get_detailed_system_prompt(self) -> str:
        """System prompt for generating detailed explanations"""
        return """You are a business communication expert who translates technical code analysis into comprehensive explanations for Product Managers.

Your task: Create a detailed, business-friendly explanation that covers:
1. What the component does (user-facing functionality)
2. How it's used in the product (practical scenarios)
3. Important limitations or requirements (business constraints)
4. How it integrates with other features (business workflows)

Rules:
- Avoid technical terms like "props", "imports", "functions", "state", "hooks"
- Instead of file paths, describe WHERE in the product (e.g., "checkout flow", "user dashboard")
- Focus on business logic, user experience, and practical implications
- Use analogies when helpful
- Structure with clear sections and bullet points
- Explain in terms that enable business decisions

Example:
TECHNICAL: "Located in src/components/PaymentButton.tsx. Imports PaymentProcessor from services/..."
DETAILED: "The Payment Button is used in the checkout process to finalize customer purchases. It appears on:
- Shopping cart checkout page
- Quick buy flows
- Subscription renewal screens

When clicked, it processes the payment and shows a confirmation message. If the payment fails, it displays an error and allows the customer to try again.

Business Requirements:
- Must show the exact dollar amount before processing
- Requires a valid payment method to be selected first
- Sends confirmation emails automatically on success

This component connects with the payment processing system and customer notification features."

Now translate the following technical analysis into a detailed business explanation:"""


class MockTranslatorAgent:
    """Mock translator for testing"""

    async def translate(self, technical_output: str, component_name: str) -> Tuple[str, str]:
        """Return mock translations"""
        brief = f"""The {component_name} allows users to perform a specific action in the application. It appears in various workflows and integrates with other features. This component is essential for the core user experience."""

        detailed = f"""The {component_name} is a key feature used throughout the application.

Where it's used:
- Main workflow screens
- User dashboard
- Settings and configuration areas

How it works:
When users interact with this feature, it processes their input and provides immediate feedback. The system validates the information and either completes the action or shows helpful error messages.

Business Requirements:
- Users must be logged in to access this feature
- Certain permissions may be required
- Data is validated before processing

Integration:
This feature connects with other parts of the system to provide a seamless experience. It works alongside related features to support the overall business workflow.

This is mock data for development purposes."""

        return brief, detailed
