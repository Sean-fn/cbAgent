"""
Idea Coverage Judge - LLM-based judge that checks if key ideas are covered
Uses OpenAI API to determine which ground truth ideas appear in the answer
"""

import json
from typing import List
from openai import AsyncOpenAI
from src.evaluation.judges.base import BaseJudge
from src.evaluation.models import GroundTruth, IdeaCoverageResult


class IdeaCoverageJudge(BaseJudge):
    """LLM-based judge that checks if key ideas are covered in answer"""

    def __init__(self, api_key: str, model: str = "gpt-5-nano"):
        """
        Initialize the idea coverage judge

        Args:
            api_key: OpenAI API key
            model: Model to use for judging (default: gpt-5-nano)
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def evaluate(
        self,
        answer: str,
        ground_truth: GroundTruth,
        question: str
    ) -> IdeaCoverageResult:
        """
        Check which key ideas are covered in the answer

        Args:
            answer: The answer to evaluate
            ground_truth: Ground truth containing key ideas
            question: Original question for context

        Returns:
            IdeaCoverageResult with coverage metrics
        """
        prompt = self._build_judge_prompt(
            question=question,
            answer=answer,
            key_ideas=ground_truth.key_ideas
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ]
        )

        # Parse structured JSON response
        result = json.loads(response.choices[0].message.content)

        ideas_found = result["ideas_found"]
        ideas_missing = result["ideas_missing"]
        coverage_score = len(ideas_found) / len(ground_truth.key_ideas) if ground_truth.key_ideas else 0.0

        return IdeaCoverageResult(
            ideas_found=ideas_found,
            ideas_missing=ideas_missing,
            coverage_score=coverage_score,
            reasoning=result["reasoning"]
        )

    def _get_system_prompt(self) -> str:
        """System prompt for idea coverage judging"""
        return """You are an evaluation judge for a component query system.

Your task: Check whether specific key ideas appear in the given answer.

For each key idea, determine if it is PRESENT or ABSENT in the answer.
- PRESENT: The idea is clearly expressed, even if using different words
- ABSENT: The idea is not mentioned or cannot be inferred

Be lenient with paraphrasing but strict about actual presence of the concept.

Return your evaluation in JSON format:
{
  "ideas_found": ["idea 1", "idea 2", ...],
  "ideas_missing": ["idea 3", ...],
  "reasoning": "Brief explanation of your judgment"
}"""

    def _build_judge_prompt(
        self,
        question: str,
        answer: str,
        key_ideas: List[str]
    ) -> str:
        """Build the evaluation prompt"""
        ideas_list = "\n".join(f"{i+1}. {idea}" for i, idea in enumerate(key_ideas))

        return f"""Original Question:
{question}

Answer to Evaluate:
{answer}

Key Ideas to Check:
{ideas_list}

For each key idea above, determine if it is present in the answer.
Return your evaluation in the specified JSON format."""
