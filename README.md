# PM Component Query System

An AI-powered CLI tool that enables Product Managers to query Git repositories for component information in plain English. The system analyzes code using OpenAI's API and translates technical details into business-friendly language.

## Features

- **Natural Language Queries**: Ask questions in plain text
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
- OpenAI API key with GPT access

## Installation

Choose either **Docker** or **Local** setup:

---

## Docker Installation
### 0. Prepare Your Repository

The system needs a Git repository to analyze:

```bash
# Clone your component library (example)
git clone https://github.com/your-org/component-library.git /path/to/repo
```


### 1. Configure Environment

```bash
# Copy the Docker environment template
cp environment.docker.template .env.docker

# Edit with your OpenAI API key
vim .env.docker
```

**Required settings in `.env.docker`:**
```bash
# Your OpenAI API key (used for both Codex CLI and GPT translation)
OPENAI_API_KEY=sk-proj-your-key-here
```

### 2. Set Repository Path

```bash
# Set the path to your Git repository on the host machine
export HOST_REPO_PATH=/path/to/your/repository
```

### 3. Run with Docker Compose

```bash
# Build and start the container
export HOST_REPO_PATH=./fms && docker-compose run --rm cb-agent-system

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
vim .env
```

**Required settings in `.env`:**
```bash
# Your OpenAI API key (used for both Codex CLI and GPT translation)
OPENAI_API_KEY=sk-proj-...
```

Optional settings:
```bash
TRANSLATOR_AGENT_MODEL=gpt-5-nano
LOG_LEVEL=INFO
```
### 3. Start the Interactive CLI

```bash
source venv/bin/activate
python -m src.main
```

## Configuration Options

### Agent Settings

- `TRANSLATOR_AGENT_MODEL`: Model for translation (default: gpt-5-vim)
- Technical analysis now uses Codex CLI directly (no model configuration needed)

## Troubleshooting

### "Repository path does not exist"
- Verify `REPO_PATH` in system env variable which points to a valid directory
- Ensure the path is a Git repository (has `.git` folder)

### "Configuration Error: openai_api_key"
- Add your OpenAI API key to `.env`:
  ```
  OPENAI_API_KEY=sk-proj-your-key-here
  ```

