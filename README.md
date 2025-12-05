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
- **Full Repository Search**: Analyzes entire codebase for comprehensive results
- **4 Query Types**:
  - Usage examples and integration steps
  - Restrictions, limitations, and constraints
  - Dependencies and requirements
  - Business rules and validation logic

## Prerequisites

- **For Docker deployment**: Docker and Docker Compose
- **For local development**: Python 3.10 or higher
- Git
- OpenAI API key with GPT-4o access

## Installation

Choose either **Docker** (recommended for easy deployment) or **Local** setup:

---

## Docker Installation (Recommended)

### 1. Configure Environment

```bash
# Copy the Docker environment template
cp environment.docker.template .env.docker

# Edit with your OpenAI API key
nano .env.docker
```

**Required settings in `.env.docker`:**
```bash
# Your OpenAI API key (used for both Codex CLI and GPT translation)
OPENAI_API_KEY=sk-proj-your-key-here

# Container repository path (leave as-is)
REPO_PATH=/workspace/repo
```

### 2. Set Repository Path

```bash
# Set the path to your Git repository on the host machine
export HOST_REPO_PATH=/path/to/your/repository
```

### 3. Run with Docker Compose

```bash
# Build and start the container
export HOST_REPO_PATH=./fms && docker-compose run --rm pm-query-system

# The system will start automatically - no need to run 'codex login'!
```

**Benefits of Docker setup:**
- ✅ No need to run `codex login` - API key authentication is automatic
- ✅ Isolated environment with all dependencies pre-installed
- ✅ Consistent runtime across different machines
- ✅ Single OPENAI_API_KEY for both Codex and GPT translation

---

## Local Installation

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

**Required settings in `.env`:**
```bash
# Your OpenAI API key (used for both Codex CLI and GPT translation)
OPENAI_API_KEY=sk-proj-...

# Path to the Git repository you want to analyze
REPO_PATH=/path/to/your/component-library
```

Optional settings:
```bash
CODEX_LOGS_DIR=/Users/sean/.cbagent/codex_logs  # Raw Codex output logs
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
- **status**: Show repository status
- **help**: Show help message
- **exit** or **quit**: Exit the program

## How It Works

1. **Direct Query**: User query sent directly to Codex (no regex parsing)
2. **Technical Analysis**: Codex CLI analyzes the entire codebase
3. **Business Translation**: Converts technical output to PM-friendly language
4. **Progressive Disclosure**: Shows brief summary first, detailed on request

## Architecture

```
PM Query → Codex CLI (Direct Analysis)
        → Translator Agent (OpenAI GPT-4o)
        → Brief + Detailed Output
```

### Key Components

- `src/main.py`: Interactive CLI and main application
- `src/config.py`: Configuration management
- `src/agents/technical_agent.py`: Codex CLI integration (direct query passing)
- `src/agents/translator_agent.py`: Business translation
- `src/mcp/codex_server.py`: Codex MCP server connection

## Configuration Options

### Agent Settings

- `TRANSLATOR_AGENT_MODEL`: Model for translation (default: gpt-5-nano)
- Technical analysis now uses Codex CLI directly (no model configuration needed)
- `CODEX_LOGS_DIR`: Directory where raw Codex JSON outputs are saved (default: ~/.cbagent/codex_logs)

### Raw Output Logging

All raw JSON outputs from Codex CLI are automatically saved to timestamped log files in the `CODEX_LOGS_DIR` directory. This is useful for:
- Debugging Codex parsing issues
- Analyzing the raw data structure
- Auditing Codex responses

Log files are named: `codex_output_YYYYMMDD_HHMMSS_microseconds.json`

Each log file contains:
```json
{
  "timestamp": "2025-12-03T10:30:45.123456",
  "stdout": "Raw stdout from Codex CLI...",
  "stderr": "Any error output..."
}
```

## Troubleshooting

### "Repository path does not exist"
- Verify `REPO_PATH` in `.env` points to a valid directory
- Ensure the path is a Git repository (has `.git` folder)

### "Configuration Error: openai_api_key"
- Add your OpenAI API key to `.env`:
  ```
  OPENAI_API_KEY=sk-proj-your-key-here
  ```

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

- [x] Integrate with Codex CLI MCP server for better code analysis
- [ ] Add support for multiple repositories
- [ ] Export results to Markdown/PDF
- [ ] Component dependency graphs
- [ ] Integration with project management tools

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.
