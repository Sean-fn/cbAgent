# Evaluation System

Modular evaluation system for CB Agent that evaluates answer quality using LLM-as-judge approach.

## Architecture

```
src/evaluation/
├── models.py                    # Pydantic data models
├── config.py                    # Evaluation settings
├── loader.py                    # JSON test case loader
├── runner.py                    # Main orchestrator
├── cli.py                       # CLI entry point
├── judges/
│   ├── base.py                  # Base judge protocol
│   └── idea_coverage_judge.py   # LLM-based idea coverage judge
└── reporters/
    ├── base.py                  # Base reporter protocol
    └── json_reporter.py         # JSON + console reporter
```

## Quick Start

### Generate Test Cases (Interactive)

Use the dataset generator to create test cases easily:

```bash
python -m src.evaluation.generate_dataset
```

The script will:
1. Prompt for questions and answers
2. Automatically extract key ideas using LLM
3. Let you review/edit extracted ideas
4. Save to `evaluation_data/test_cases.json`

See `evaluation_data/README.md` for detailed instructions.

## Usage

### 1. Create Test Cases

**Option A: Use the interactive generator (recommended)**

```bash
python -m src.evaluation.generate_dataset
```

**Option B: Create manually**

Create `evaluation_data/test_cases.json`:

```json
{
  "test_cases": [
    {
      "id": "001",
      "question": "How does PaymentButton work?",
      "ground_truth": {
        "key_ideas": [
          "Handles payment submission",
          "Validates card info",
          "Shows loading state"
        ]
      }
    }
  ]
}
```

See `evaluation_data/test_cases.json.example` for more examples.

### 2. Run Evaluation

```bash
# From project root
python -m src.evaluation.cli
```

### 3. View Results

Results are saved to `evaluation_results/{timestamp}_evaluation_results.json` and displayed in console.

## Configuration

Environment variables (optional, defaults shown):

```bash
# Evaluation settings (prefix: EVAL_)
EVAL_JUDGE_MODEL=gpt-5-nano
EVAL_TEST_CASES_PATH=evaluation_data/test_cases.json
EVAL_RESULTS_OUTPUT_DIR=evaluation_results
EVAL_MAX_CONCURRENT_EVALUATIONS=3
EVAL_EVALUATION_TIMEOUT=900
```

## Output Format

### Console Summary

- Overview: Total cases, successful, failed, success rate
- Idea Coverage Statistics: Avg/min/max coverage by answer type
- Performance: Average execution time
- Failed test cases (if any)

### JSON Report

```json
{
  "timestamp": "2025-12-10T16:30:00",
  "total_test_cases": 10,
  "successful": 9,
  "failed": 1,
  "results": [
    {
      "test_case_id": "001",
      "question": "...",
      "answers": {
        "brief": "...",
        "detailed": "...",
        "raw": "..."
      },
      "evaluations": [
        {
          "answer_type": "brief",
          "idea_coverage": {
            "ideas_found": ["..."],
            "ideas_missing": ["..."],
            "coverage_score": 0.67,
            "reasoning": "..."
          }
        }
      ],
      "execution_time": 45.3,
      "error": null
    }
  ],
  "summary_stats": {
    "brief_avg_coverage": 0.72,
    "detailed_avg_coverage": 0.89,
    "raw_avg_coverage": 0.78,
    "avg_execution_time": 42.5
  }
}
```

## Evaluation Metrics

### Idea Coverage (Phase 1)

- **Ideas Found**: Which key ideas from ground truth appear in the answer
- **Ideas Missing**: Which key ideas are absent
- **Coverage Score**: Ratio of found to total ideas (0.0-1.0)
- **Reasoning**: LLM's explanation of judgment

Evaluates all three answer formats:
- **Brief**: 3-4 sentence summary
- **Detailed**: Comprehensive explanation
- **Raw**: Technical output from Codex

## Extensibility

### Adding New Judges (Future Phases)

```python
from src.evaluation.judges.base import BaseJudge
from src.evaluation.models import IdeaCoverageResult

class MyCustomJudge(BaseJudge):
    async def evaluate(self, answer, ground_truth, question):
        # Your evaluation logic
        return IdeaCoverageResult(...)
```

Update CLI to include new judge:

```python
judges = [
    IdeaCoverageJudge(...),
    MyCustomJudge(...)  # Add here
]
```

### Future Judge Types

- **Semantic Similarity**: BERTScore, cosine similarity, ROUGE
- **Quality Assessment**: Clarity, completeness, jargon-free scoring
- **Consistency Check**: Agreement between brief/detailed/raw

## Implementation Details

### Pipeline Integration

The runner reuses the exact production pipeline:

```python
# Get raw technical output
technical = await pm_system.technical_agent.analyze_query(question)

# Get translations in parallel
brief, detailed = await asyncio.gather(
    pm_system.translator_agent._generate_brief(technical, question),
    pm_system.translator_agent._generate_detailed(technical, question)
)
```

### Concurrency Control

- Default: 3 concurrent test evaluations
- Configurable via `EVAL_MAX_CONCURRENT_EVALUATIONS`
- Uses asyncio semaphore for limiting

### Error Handling

- Errors are captured per test case
- Failed tests don't stop evaluation
- Error details saved in results JSON

## Dependencies

All dependencies already in `requirements.txt`:
- `openai` (AsyncOpenAI client)
- `pydantic` + `pydantic-settings`
- `rich` (console, tables, progress)
- `asyncio`

No new dependencies required for Phase 1.
