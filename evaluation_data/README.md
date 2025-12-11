# Evaluation Data Directory

This directory contains test cases for the evaluation system.

## Files

- `test_cases.json` - Your test cases (created by you)
- `test_cases.json.example` - Example test cases format
- `batch_input.txt.example` - Example batch input format

## Creating Test Cases

You have two options to create test cases:

### Option 1: Interactive Mode (Recommended)

Use the interactive dataset generator script:

```bash
python -m src.evaluation.generate_dataset
```

**How it works:**
1. Enter a question
2. Paste the ground truth answer (the ideal answer you expect)
3. The LLM automatically extracts key ideas from the answer
4. Review and optionally edit the extracted ideas
5. Repeat to add more test cases
6. Saves to `evaluation_data/test_cases.json`

**Example Session:**
```
━━━ Test Case #1 ━━━

Question: How does the PaymentButton work?

Ground Truth Answer (paste answer, then press Enter twice):
The PaymentButton handles payment submission, validates card info,
shows loading states, and displays success/error messages.
[Press Enter twice]

Extracting key ideas...

Extracted Key Ideas:
  1. Handles payment submission
  2. Validates card information
  3. Shows loading states during processing
  4. Displays success or error messages

Edit key ideas? [y/N]: n

✓ Test case added!

Add another test case? [Y/n]:
```

### Option 2: Batch Mode

Create a text file with Q&A pairs and process them all at once:

```bash
python -m src.evaluation.generate_dataset batch_input.txt
```

**Input Format** (`batch_input.txt`):
```
Q: First question here?
A: First answer here...
Can be multiple lines.

Q: Second question here?
A: Second answer here...
Also multiple lines.
```

See `batch_input.txt.example` for a complete example.

### Option 3: Manual Creation

Create `test_cases.json` manually:

```json
{
  "test_cases": [
    {
      "id": "001",
      "question": "Your question here?",
      "ground_truth": {
        "key_ideas": [
          "First key idea",
          "Second key idea",
          "Third key idea"
        ]
      }
    }
  ]
}
```

## Test Case Guidelines

### Good Key Ideas

✅ **Do:**
- Keep ideas concise (5-15 words)
- Focus on business concepts, not technical details
- Make each idea independently verifiable
- Use 3-7 key ideas per test case
- Express core functionality and behavior

✅ **Examples:**
- "Handles payment submission"
- "Validates card information before processing"
- "Shows loading state during transaction"
- "Displays error messages on failure"

❌ **Don't:**
- Include implementation details: "Uses React hooks to manage state"
- Be too vague: "Does things with data"
- Combine multiple concepts: "Validates input and submits to API and shows results"
- Use overly technical jargon: "Implements observer pattern for state management"

### Question Types

Your questions can test different aspects:

1. **Usage Questions**
   - "How do I use the PaymentButton?"
   - "What does the SearchBar do?"

2. **Business Rules**
   - "What are the restrictions for UserProfile?"
   - "What validation rules apply to LoginForm?"

3. **Dependencies**
   - "What does CheckoutFlow depend on?"
   - "What services does PaymentButton integrate with?"

4. **Integration**
   - "How does OrderSummary connect with the cart?"
   - "What happens when PaymentButton is clicked?"

## Running Evaluations

Once you have test cases:

```bash
python -m src.evaluation.cli
```

Results will be saved to `../evaluation_results/`

## Tips

1. **Start Small**: Begin with 3-5 test cases to validate your approach
2. **Iterate**: Run evaluations, review results, refine test cases
3. **Be Specific**: More specific key ideas = more accurate evaluation
4. **Test Edge Cases**: Include both common and unusual scenarios
5. **Keep Ground Truth Updated**: As your system evolves, update test cases

## Troubleshooting

**"OPENAI_API_KEY not found"**
- Ensure you have a `.env` file in the project root
- Add: `OPENAI_API_KEY=your-api-key-here`

**Key ideas seem wrong**
- Use interactive mode and edit the extracted ideas
- The LLM suggestion is just a starting point
- Manual refinement often produces better results

**File exists error**
- The script will ask before overwriting
- Choose to save with timestamp to keep both versions
