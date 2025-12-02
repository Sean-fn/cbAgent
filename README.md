# PM Component Query System

An AI-powered CLI tool that enables Product Managers to query Git repositories for component information in plain English. The system analyzes code using OpenAI's API and translates technical details into business-friendly language.

## Overview

This system allows non-technical stakeholders to ask questions about components like:
- "How do I use the PaymentButton?"
- "What are the restrictions for UserProfile?"
- "What does LoginForm depend on?"
- "What are the business rules for CheckoutFlow?"

And get answers in clear, business-focused language without technical jargon.

## Features

- **Natural Language Queries**: Ask questions in plain English
- **Progressive Disclosure**: Brief summaries with optional detailed explanations
- **Smart Caching**: Auto-invalidates when repository changes (via `git pull`)
- **Full Repository Search**: Analyzes entire codebase for comprehensive results
- **4 Query Types**:
  - Usage examples and integration steps
  - Restrictions, limitations, and constraints
  - Dependencies and requirements
  - Business rules and validation logic

## Prerequisites

- Python 3.10 or higher
- Node.js 18+ (for future Codex CLI integration)
- Git
- OpenAI API key with GPT-4o access

## Installation

### 1. Clone and Setup

```bash
cd /Users/sean/work/cbAgent

# Activate virtual environment
source venv/bin/activate

# Install dependencies (already done if you followed setup)
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the template
cp env.template .env

# Edit .env with your settings
nano .env
```

Required settings in `.env`:
```bash
# Your OpenAI API key
OPENAI_API_KEY=sk-proj-...

# Path to the Git repository you want to analyze
REPO_PATH=/path/to/your/component-library
```

Optional settings:
```bash
CACHE_DIR=/Users/sean/work/cbAgent/.cache
CACHE_ENABLED=true
CACHE_TTL_DAYS=7
CACHE_AUTO_INVALIDATE=true
TECHNICAL_AGENT_MODEL=gpt-5-nano
TRANSLATOR_AGENT_MODEL=gpt-5-nano
LOG_LEVEL=INFO
```

### 3. Prepare Your Repository

The system needs a Git repository to analyze:

```bash
# Clone your component library (example)
git clone https://github.com/your-org/component-library.git /path/to/repo

# Update REPO_PATH in .env to point to this repository
```

## Usage

### Start the Interactive CLI

```bash
source venv/bin/activate
python -m src.main
```

### Example Session

```
PM Component Query System
Repository: /Users/sean/projects/my-components
Status: Up to date (commit: abc123d)

❯ How do I use the PaymentButton?

Analyzing PaymentButton...
✓

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Component: PaymentButton
Query Type: Find examples, parameters, and integration steps
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 Quick Summary

The Payment Button allows customers to complete purchases by
entering their payment information. When clicked, it processes
the transaction and shows a confirmation message. This component
is used throughout the checkout process.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Want more details?
   Type 'more' to see full explanation, or try:
   - What are the restrictions for PaymentButton?
   - What does PaymentButton depend on?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❯ more

📋 Detailed Explanation

[Comprehensive business-friendly explanation with examples,
use cases, integration details, and business context...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❯ exit
Goodbye!
```

### Available Commands

- **Query**: Just type your question naturally
- **more**: Show detailed explanation for the last query
- **status**: Show cache and repository status
- **cache clear**: Clear all cached results
- **help**: Show help message
- **exit** or **quit**: Exit the program

## How It Works

1. **Query Parsing**: Detects query type and extracts component name
2. **Cache Check**: Looks for existing cached analysis
3. **Technical Analysis**: Uses OpenAI to analyze the codebase
4. **Business Translation**: Converts technical output to PM-friendly language
5. **Progressive Disclosure**: Shows brief summary first, detailed on request
6. **Auto-Invalidation**: Cache automatically clears when repository changes

## Architecture

```
PM Query → Parser → Cache → Technical Agent (OpenAI GPT-4o)
                          → Translator Agent (OpenAI GPT-4o)
                          → Brief + Detailed Output
```

### Key Components

- `src/main.py`: Interactive CLI and main application
- `src/config.py`: Configuration management
- `src/cache.py`: Persistent cache with Git tracking
- `src/agents/technical_agent.py`: Code analysis using OpenAI
- `src/agents/translator_agent.py`: Business translation
- `src/queries/parser.py`: Natural language query parsing
- `src/queries/templates.py`: Query templates for each type

## Configuration Options

### Cache Settings

- `CACHE_ENABLED`: Enable/disable caching (default: true)
- `CACHE_TTL_DAYS`: Days before cache expires (default: 7)
- `CACHE_AUTO_INVALIDATE`: Auto-clear cache on git changes (default: true)

### Agent Settings

- `TECHNICAL_AGENT_MODEL`: Model for code analysis (default: gpt-5-nano)
- `TRANSLATOR_AGENT_MODEL`: Model for translation (default: gpt-5-nano)

### Repository Updates

After running `git pull` in your repository:
- If `CACHE_AUTO_INVALIDATE=true`: Cache automatically invalidates
- If `CACHE_AUTO_INVALIDATE=false`: Run `cache clear` manually

## Troubleshooting

### "Repository path does not exist"
- Verify `REPO_PATH` in `.env` points to a valid directory
- Ensure the path is a Git repository (has `.git` folder)

### "Configuration Error: openai_api_key"
- Add your OpenAI API key to `.env`:
  ```
  OPENAI_API_KEY=sk-proj-your-key-here
  ```

### Cache not invalidating after git pull
- Check `CACHE_AUTO_INVALIDATE=true` in `.env`
- Or manually run: `cache clear`

### Slow queries
- First query for a component takes longer (no cache)
- Subsequent queries are much faster (cached)
- Cache persists across sessions

## Development

### Project Structure

```
/Users/sean/work/cbAgent/
├── .env                    # Your configuration
├── env.template            # Environment template
├── requirements.txt        # Python dependencies
├── src/
│   ├── main.py            # Entry point
│   ├── config.py          # Settings
│   ├── cache.py           # Cache layer
│   ├── agents/            # AI agents
│   ├── mcp/               # Codex integration (future)
│   ├── queries/           # Query handling
│   └── utils/             # Utilities
└── tests/                 # Test files
```

### Running Tests

```bash
source venv/bin/activate
pytest tests/
```

## Roadmap

- [ ] Integrate with Codex CLI MCP server for better code analysis
- [ ] Add support for multiple repositories
- [ ] Export results to Markdown/PDF
- [ ] Component dependency graphs
- [ ] Integration with project management tools

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.
