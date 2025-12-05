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

    async def translate(self, technical_output: str, user_input: str) -> Tuple[str, str]:
        """
        Translate technical output to business-friendly language

        Args:
            technical_output: Technical analysis from TechnicalAgent

        Returns:
            Tuple of (brief_summary, detailed_explanation)
        """
        try:
            # Generate brief summary
            brief = await self._generate_brief(technical_output, user_input)

            # Generate detailed explanation
            detailed = await self._generate_detailed(technical_output, user_input)

            return brief, detailed

        except Exception as e:
            raise RuntimeError(f"Translation failed: {str(e)}")

    async def _generate_brief(self, technical_output: str, user_input: str) -> str:
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
                    "content": f"User Input: {user_input}"
                },
                {
                    "role": "user",
                    "content": f"\n\nTechnical Analysis:\n{technical_output}"
                }
            ],
        )

        return response.choices[0].message.content.strip()

    async def _generate_detailed(self, technical_output: str, user_input: str) -> str:
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
                    "content": f"User Input: {user_input}"
                },
                {
                    "role": "user",
                    "content": f"\n\nTechnical Analysis:\n{technical_output}"
                }
            ],
        )

        return response.choices[0].message.content.strip()

    def _get_brief_system_prompt(self) -> str:
        """System prompt for generating brief summaries"""
        return """您是一位商務溝通專家，負責將技術程式碼分析翻譯成產品經理能理解的清晰摘要。

**您的任務：** 撰寫一份簡潔的 3-4 句話摘要，解釋該元件的**功能**以及從**商業角度來看的重要性**。

---

**規則：**
* **不要**使用技術術語（例如：`props`、`functions`、`imports` 等）。
* **不要**使用檔案路徑或程式碼語法。
* 專注於**使用者可見的行為**和**商業價值**。
* 使用簡單、口語化的語言。
* 以非技術人員能理解的方式解釋。

---

**範例：**
* **技術說明：** "The PaymentButton component accepts an `amount` prop (type: number) and `onSuccess` callback..."
* **簡潔摘要：** "付款按鈕允許客戶點擊以處理付款，從而完成購買。它會處理支付金額，並在交易成功或失敗時通知系統。此元件在整個結帳流程中都會被使用。"

---
現在，請將以下技術分析翻譯成一份簡潔的商業摘要：
"""
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
        return """**您是商務溝通專家，負責將技術程式碼分析轉譯成供產品經理理解的全面性解釋。**

**您的任務：** 建立一份詳盡、適合商務人士閱讀的解釋，內容須涵蓋：

1.  該組件的用途（**使用者可見的功能**）
2.  該組件在產品中的使用方式（**實際應用情境**）
3.  重要的限制或要求（**業務約束**）
4.  該組件如何與其他功能整合（**業務工作流程**）

**規則：**

* **避免**使用「props」、「imports」、「functions」、「state」、「hooks」等技術術語。
* **不要**使用檔案路徑，而是描述在產品中的**何處**（例如：「結帳流程」、「用戶儀表板」）。
* 專注於**業務邏輯**、**用戶體驗**和**實際影響**。
* 必要時可使用**類比**。
* 以清晰的**章節標題**和**項目符號**結構化內容。
* 使用能幫助**業務決策**的術語進行解釋。

**範例：**

**技術描述：** 「位於 `src/components/PaymentButton.tsx`。從 `services/` 導入 `PaymentProcessor`...」

**詳盡的商務解釋：** 「**付款按鈕**用於結帳流程中，以完成顧客購買。它出現在：
* 購物車結帳頁面
* 快速購買流程
* 訂閱續費畫面

當點擊時，它會處理付款並顯示確認訊息。如果付款失敗，則會顯示錯誤並允許顧客再次嘗試。

**業務要求：**
* 在處理前必須顯示確切的金額
* 要求必須先選擇一個有效的付款方式
* 成功時會自動發送確認電子郵件

此組件連接到**付款處理系統**和**客戶通知功能**。」"""
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
