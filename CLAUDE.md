- DO NOT reference any files in @repo/ @more_repo/

# CB Agent - PM Component Query System

## Project Overview

**Purpose**: AI-powered CLI tool that enables Product Managers to query Git repositories for component information in plain English. Analyzes code using OpenAI's Codex and translates technical details into business-friendly language.

**Scale**: Medium Project

---

## Architecture

### Core Pipeline (3 Stages)

```
User Input (Natural Language)
    ↓
[Stage 1] TechnicalAgent
    • Passes query directly to Codex CLI
    • Returns: Plain text technical analysis
    ↓
[Stage 2] TranslatorAgent (Parallel)
    • Brief generation: 3-4 sentence summary via GPT
    • Detailed generation: Full business explanation via GPT
    ↓
[Stage 3] Progressive Disclosure (UI)
    • Displays brief immediately
    • Waits for detailed in background
    • User can request "more" or "raw" details
```

### Component Responsibilities

#### **TechnicalAgent** (`src/agents/technical_agent.py`)
- **Role**: Code analysis orchestration
- **Method**: Uses OpenAI's Codex CLI (not OpenAI API directly)
- **Authentication**: Session-based via `codex login` (no API key)
- **Input**: Natural language query wrapped in system prompt
- **Output**: Plain string from `.msg.message` field
- **System Prompt**: "Hoss" persona—senior PM translator, not technical jargon
- **Dependencies**: `CodexExecutor` class

#### **TranslatorAgent** (`src/agents/translator_agent.py`)
- **Role**: Convert technical output to PM language
- **Method**: AsyncOpenAI client with two concurrent tasks
- **Models**: Configurable (default: "gpt-5-nano")
- **Prompts**: Two system prompts (brief vs. detailed)
- **Features**:
  - Removes technical jargon (props, imports, functions, code paths)
  - Focuses on business value and user-facing behavior
  - Respects input language (multilingual support)
  - Progressive disclosure structure

#### **CodexExecutor** (`src/codex/codex_executor.py`)
- **Role**: Subprocess management for Codex CLI
- **Method**: Async subprocess with timeout handling
- **Script**: Wraps `bash codex_script.sh` with jq JSON extraction
- **Output Parsing**:
  - Tries to extract `.item | select(.type == "agent_message") | .text`
  - Falls back to `.msg.message` if agent_message not found
  - Returns plain text string
- **Error Handling**:
  - `CodexTimeoutError`: Query exceeds timeout (default 600s)
  - `CodexAuthError`: Authentication failure
  - `CodexParseError`: JSON parsing issues

#### **SessionState** (`src/main.py`)
- Tracks last query, detailed output, and technical output
- Enables "more" and "raw" commands

---

## Technology Stack

- **Language**: Python 3.10+ (asyncio-based)
- **Core Dependencies**:
  - OpenAI SDK (for GPT translation)
  - Codex CLI (for code analysis)
  - Pydantic + Pydantic Settings (configuration/validation)
  - Rich + Prompt Toolkit (CLI/UX)
  - GitPython (repo validation)
  - pytest + pytest-asyncio (testing)
- **Deployment**: Docker with multi-stage builds

---

## Directory Structure

```
/Users/sean/work/cbAgent/
├── src/
│   ├── main.py                    # Entry point: async CLI loop
│   ├── config.py                  # Pydantic settings, repo validation
│   ├── agents/
│   │   ├── technical_agent.py     # Codex CLI orchestration
│   │   └── translator_agent.py    # GPT-based business translation
│   ├── codex/
│   │   ├── codex_executor.py      # Async subprocess management
│   │   └── codex_script.sh        # Bash wrapper for codex CLI
│   ├── queries/
│   │   ├── parser.py              # Query type detection (unused)
│   │   └── templates.py           # Query templates (unused)
│   └── utils/                     # Empty directory
├── docker/
│   └── entrypoint.sh              # Container startup
├── Dockerfile                     # Multi-stage Python 3.11 build
├── docker-compose.yml             # Service orchestration
├── requirements.txt               # Dependencies
└── env.template / environment.docker.template
```

---

## Configuration System (`src/config.py`)

- **Framework**: Pydantic Settings
- **Source**: Environment variables + `.env` file
- **Validation**: Checks repo path exists and contains `.git`
- **Settings**:
  - `openai_api_key` (required)
  - `repo_path` (default: `/workspace/repo`)
  - `codex_timeout` (default: 600s for complex queries)
  - `translator_agent_model` (default: "gpt-5-nano")
  - `max_retries` (default: 3)

---

## LLM Call Patterns

### Codex Execution Flow (Technical Analysis)
```bash
bash codex_script.sh <prompt>
  └─ codex exec --json <prompt> --sandbox read-only --skip-git-repo-check
     └─ JSON output
        └─ jq extraction (.item or .msg.message)
           └─ Plain text string
```

**Implementation**:
- Uses Codex CLI directly (subprocess, not SDK)
- Async execution with `asyncio.create_subprocess_exec()`
- Timeout protection with `asyncio.wait_for()`
- Error suppression on stderr

### OpenAI API Calls (Translation)
```python
AsyncOpenAI(api_key=config.openai_api_key)
  └─ client.chat.completions.create(
       model="gpt-5-nano",
       messages=[
         {"role": "system", "content": prompt},
         {"role": "user", "content": technical_output}
       ]
     )
```

**Parallel Execution**:
- Brief and detailed generated simultaneously via `await asyncio.gather()`
- Brief shown immediately; detailed awaited in background

### System Prompts Architecture

Two distinct system prompts:

1. **Technical Agent's "Hoss" Prompt** (in `technical_agent.py`):
   - Target: Codex CLI
   - Persona: Senior PM & Business Analyst
   - Focus: Business logic, operational scenarios, not code
   - Guidance: Translation thinking model (What → Why → Hidden Logic)
   - Constraints: Avoid code paths, technical verbs, jargon

2. **TranslatorAgent System Prompts**:
   - **Brief Prompt**: Create 3-4 sentence summary, no jargon, focus on user behavior
   - **Detailed Prompt**: Comprehensive business explanation with sections, no technical terms

---

## Data Formats

### Configuration (Pydantic)
```python
class Settings(BaseSettings):
    openai_api_key: str
    repo_path: Path = Path("/workspace/repo")
    codex_timeout: int = 600
    translator_agent_model: str = "gpt-5-nano"
    max_retries: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
```

### Codex CLI Output (JSON)
- Returned as plain string after jq extraction
- Structure: `{.item | select(.type == "agent_message") | .text}` or `.msg.message`
- No structured parsing—returned as-is

### Query Types (Unused Parser)
```python
class QueryType(Enum):
    USAGE = "usage"
    RESTRICTIONS = "restrictions"
    DEPENDENCIES = "dependencies"
    BUSINESS_RULES = "business_rules"
    UNKNOWN = "unknown"
```

**Note**: The query parser exists but is **not used** in the current implementation. The system passes queries directly to Codex without parsing.

---

## Pipeline Patterns

### Pipeline Architecture
1. **Input**: User natural language query
2. **Processing**:
   - TechnicalAgent analyzes via Codex (async subprocess)
   - TranslatorAgent translates via OpenAI (parallel brief + detailed)
3. **Output**: Progressive disclosure (brief first, detailed on demand)
4. **Storage**: Session state for "more"/"raw" commands

### Error Handling Patterns
- **Custom Exceptions**:
  - `CodexTimeoutError`
  - `CodexAuthError`
  - `CodexExecutorError`
  - `CodexParseError`
- **Propagation**: Caught in `process_query()`, displayed to user
- **Async Context**: Exceptions bubble from subprocess/OpenAI calls

### Async Patterns
- **asyncio.create_subprocess_exec()**: Run Codex in subprocess
- **asyncio.wait_for()**: Add timeout protection
- **asyncio.gather()**: Parallel brief + detailed generation
- **run_in_executor()**: Prompt input in executor (blocking I/O)

---

## Environment Management

- `.env` file for local development
- `.env.docker` for Docker deployment
- Pydantic Settings with environment variable loading
- Variable prefix: `ENC_` for encrypted secrets

---

## Docker & Deployment

### Container Setup
- **Base Image**: Python 3.11-slim
- **Build Strategy**: Multi-stage (builder + runtime)
- **Codex Integration**: Downloaded from GitHub releases in builder stage
- **Volume Mounting**: `/workspace/repo` for repository access
- **User**: Non-root `appuser` (1000:1000)

### Environment Variables
```
OPENAI_API_KEY=sk-proj-...
REPO_PATH=/workspace/repo (container path)
CODEX_TIMEOUT=600
TRANSLATOR_AGENT_MODEL=gpt-5-nano
```

### Entrypoint Flow
```bash
/usr/local/bin/entrypoint.sh
  └─ python -m src.main
     └─ Async CLI loop
```

---

## Testing Infrastructure

**Current State**: No test files or evaluation infrastructure in main project.

**Testing Framework**: pytest + pytest-asyncio configured in requirements.txt

---

## Key Design Principles

1. **Progressive Disclosure**: Show brief immediately, detailed on demand
2. **Business-First Language**: Remove all technical jargon
3. **Async-First**: All I/O operations use asyncio
4. **Clean Separation**: TechnicalAgent ↔ TranslatorAgent separation
5. **Strong Configuration**: Pydantic validation for all settings
6. **Docker-First**: Container as primary deployment model