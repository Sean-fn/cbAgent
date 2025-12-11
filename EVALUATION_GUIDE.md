# Evaluation System - Quick Start Guide

Complete guide to using the CB Agent evaluation system.

## Overview

The evaluation system measures how well the CB Agent answers questions by comparing against ground truth using **LLM-as-judge** for idea coverage.

**What it evaluates:**
- ✅ Brief answers (3-4 sentence summaries)
- ✅ Detailed answers (comprehensive explanations)
- ✅ Raw answers (technical Codex output)

**Metrics:**
- Ideas found vs. missing from ground truth
- Coverage score (0.0-1.0)
- LLM reasoning for judgments

---

## Step-by-Step Usage

### Step 1: Generate Test Cases (Interactive)

Run the dataset generator:

```bash
python -m src.evaluation.generate_dataset
```

**Example session:**

```
━━━ Test Case #1 ━━━

Question: How does the PaymentButton work?

Ground Truth Answer (paste answer, then press Enter twice):
The PaymentButton handles payment submission by validating
card information, showing loading states during processing,
and displaying success or error messages to users.

[Press Enter twice]

Extracting key ideas...

Extracted Key Ideas:
  1. Handles payment submission
  2. Validates card information
  3. Shows loading states during processing
  4. Displays success or error messages

Edit key ideas? [y/N]: n

✓ Test case added!

Add another test case? [Y/n]: n

✓ Dataset saved to evaluation_data/test_cases.json
Total test cases: 1
```

### Step 2: Review Generated Test Cases

Check the generated file:

```bash
cat evaluation_data/test_cases.json
```

Expected format:

```json
{
  "test_cases": [
    {
      "id": "001",
      "question": "How does the PaymentButton work?",
      "ground_truth": {
        "key_ideas": [
          "Handles payment submission",
          "Validates card information",
          "Shows loading states",
          "Displays success or error messages"
        ]
      }
    }
  ]
}
```

### Step 3: Run Evaluation

Execute the evaluation:

```bash
python -m src.evaluation.cli
```

**Output:**

```
Evaluation System

Loading test cases from evaluation_data/test_cases.json...
✓ Loaded 3 test cases

Initializing PM Query System...
✓ PM Query System initialized

Initializing judges...
✓ Initialized 1 judge(s)

Starting Evaluation
Total test cases: 3
Concurrent executions: 3

Evaluating... ━━━━━━━━━━━━━━━━━━━━ 100% 3/3

================================================================================
                            Evaluation Summary
================================================================================

                                  Overview
┏━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric       ┃ Value ┃
┡━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Cases  │ 3     │
│ Successful   │ 3     │
│ Failed       │ 0     │
│ Success Rate │ 100%  │
└──────────────┴───────┘

                      Idea Coverage Statistics
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Answer Type ┃ Avg Coverage ┃ Min Coverage ┃ Max Coverage ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ Brief       │ 72.00%       │ 50.00%       │ 100.00%      │
│ Detailed    │ 89.00%       │ 75.00%       │ 100.00%      │
│ Raw         │ 78.00%       │ 66.67%       │ 100.00%      │
└─────────────┴──────────────┴──────────────┴──────────────┘

Average Execution Time: 42.5s

✓ Results saved to: evaluation_results/20251210_163000_evaluation_results.json

================================================================================
```

### Step 4: Review Results

Open the detailed JSON report:

```bash
cat evaluation_results/20251210_163000_evaluation_results.json
```

**Key sections:**

```json
{
  "results": [
    {
      "test_case_id": "001",
      "question": "How does the PaymentButton work?",
      "evaluations": [
        {
          "answer_type": "brief",
          "idea_coverage": {
            "ideas_found": ["Handles payment submission", "Shows loading states"],
            "ideas_missing": ["Validates card information", "Displays messages"],
            "coverage_score": 0.5,
            "reasoning": "The brief answer covers submission and loading but misses validation and user feedback"
          }
        },
        {
          "answer_type": "detailed",
          "idea_coverage": {
            "ideas_found": ["All ideas"],
            "ideas_missing": [],
            "coverage_score": 1.0,
            "reasoning": "Detailed answer comprehensively covers all key ideas"
          }
        }
      ]
    }
  ],
  "summary_stats": {
    "brief_avg_coverage": 0.72,
    "detailed_avg_coverage": 0.89,
    "raw_avg_coverage": 0.78
  }
}
```

---

## Alternative: Batch Mode

Create multiple test cases from a text file:

### 1. Create Input File

`my_questions.txt`:

```
Q: How does the PaymentButton work?
A: The PaymentButton handles payment submission by validating
card information, showing loading states, and displaying messages.

Q: What are the LoginForm requirements?
A: LoginForm requires valid email format and password strength.
It includes rate limiting and session management.
```

### 2. Generate Dataset

```bash
python -m src.evaluation.generate_dataset my_questions.txt
```

### 3. Run Evaluation

```bash
python -m src.evaluation.cli
```

---

## Configuration Options

Optional environment variables (add to `.env`):

```bash
# Judge settings
EVAL_JUDGE_MODEL=gpt-5-nano          # Model for evaluation

# Paths
EVAL_TEST_CASES_PATH=evaluation_data/test_cases.json
EVAL_RESULTS_OUTPUT_DIR=evaluation_results

# Performance
EVAL_MAX_CONCURRENT_EVALUATIONS=3    # Parallel test execution
EVAL_EVALUATION_TIMEOUT=900          # 15 minutes per test
```

---

## Tips for Good Test Cases

### ✅ Good Key Ideas

```json
{
  "key_ideas": [
    "Handles payment submission",              // Specific action
    "Validates card information",              // Clear requirement
    "Shows loading state during processing",   // Observable behavior
    "Displays error messages on failure"       // User feedback
  ]
}
```

### ❌ Poor Key Ideas

```json
{
  "key_ideas": [
    "Uses React hooks to manage state",        // Too technical
    "Does payment stuff",                      // Too vague
    "Validates input and submits to API",      // Multiple concepts
    "Implements observer pattern"              // Implementation detail
  ]
}
```

### Guidelines

1. **3-7 ideas per test**: Enough to be comprehensive, not overwhelming
2. **Business language**: Focus on what, not how
3. **Independently verifiable**: Each idea stands alone
4. **Concise**: 5-15 words per idea
5. **Specific**: Avoid vague terms like "handles data" or "processes things"

---

## Common Use Cases

### Use Case 1: Validate New Features

```bash
# Add test cases for new feature
python -m src.evaluation.generate_dataset

# Run evaluation
python -m src.evaluation.cli

# Check if answers cover all key points
cat evaluation_results/*.json | jq '.summary_stats'
```

### Use Case 2: Compare Versions

```bash
# Baseline
python -m src.evaluation.cli
mv evaluation_results/*.json evaluation_results/baseline.json

# After changes
python -m src.evaluation.cli
mv evaluation_results/*.json evaluation_results/new_version.json

# Compare coverage scores
diff <(jq '.summary_stats' evaluation_results/baseline.json) \
     <(jq '.summary_stats' evaluation_results/new_version.json)
```

### Use Case 3: Find Weak Areas

```bash
# Run evaluation
python -m src.evaluation.cli

# Find lowest coverage
jq '.results[] | select(.evaluations[].idea_coverage.coverage_score < 0.7)' \
   evaluation_results/*.json
```

---

## Troubleshooting

### Error: "OPENAI_API_KEY not found"

**Solution:**
```bash
# Check .env file
cat .env | grep OPENAI_API_KEY

# If missing, add it
echo "OPENAI_API_KEY=your-key-here" >> .env
```

### Error: "Test cases file not found"

**Solution:**
```bash
# Generate test cases first
python -m src.evaluation.generate_dataset

# Or create manually
cat > evaluation_data/test_cases.json <<EOF
{
  "test_cases": [...]
}
EOF
```

### Low Coverage Scores

**Possible causes:**
1. Ground truth ideas too specific
2. System not covering all aspects
3. Ideas not aligned with what system focuses on

**Solutions:**
- Review and adjust ground truth ideas
- Check if questions are clear
- Verify system is working correctly

### Evaluation Takes Too Long

**Solutions:**
```bash
# Reduce concurrent evaluations
export EVAL_MAX_CONCURRENT_EVALUATIONS=1

# Or reduce test cases temporarily
jq '.test_cases |= .[0:3]' evaluation_data/test_cases.json > test_small.json
EVAL_TEST_CASES_PATH=test_small.json python -m src.evaluation.cli
```

---

## Next Steps

### Improve Test Coverage

1. Add more diverse questions
2. Include edge cases
3. Test different question types (usage, rules, dependencies)

### Analyze Results

1. Identify patterns in missing ideas
2. Compare brief vs detailed coverage
3. Track improvements over time

### Extend System (Future)

Phase 2 - Add semantic similarity:
- BERTScore
- Cosine similarity
- ROUGE-L

Phase 3 - Add quality metrics:
- Clarity (1-5)
- Completeness (1-5)
- Jargon-free (1-5)

See `src/evaluation/README.md` for extensibility details.

---

## File Structure

```
/Users/sean/work/cbAgent/
├── src/evaluation/
│   ├── generate_dataset.py     # Dataset generator
│   ├── cli.py                  # Evaluation runner
│   └── README.md               # Technical docs
├── evaluation_data/
│   ├── test_cases.json         # Your test cases
│   ├── test_cases.json.example # Example format
│   ├── batch_input.txt.example # Batch mode example
│   └── README.md               # Dataset creation guide
├── evaluation_results/
│   └── *.json                  # Generated reports
└── EVALUATION_GUIDE.md         # This guide
```

---

## Quick Reference

```bash
# Generate test cases (interactive)
python -m src.evaluation.generate_dataset

# Generate from batch file
python -m src.evaluation.generate_dataset questions.txt

# Run evaluation
python -m src.evaluation.cli

# View results
cat evaluation_results/*.json | jq '.summary_stats'

# Check specific test case
jq '.results[] | select(.test_case_id == "001")' evaluation_results/*.json
```

---

For more details:
- Technical documentation: `src/evaluation/README.md`
- Dataset creation: `evaluation_data/README.md`
- Architecture plan: `~/.claude/plans/vectorized-munching-boot.md`
