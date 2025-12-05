#!/bin/bash
# Entrypoint script for PM Component Query System Docker container
# Validates environment and dependencies before starting the application

set -e

echo "🔍 Validating Docker environment..."

# Check 1: OpenAI API key (used for both OpenAI API and Codex CLI)
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ ERROR: OPENAI_API_KEY environment variable is not set!"
    echo ""
    echo "Please provide your OpenAI API key:"
    echo "  --env OPENAI_API_KEY=sk-proj-..."
    echo "Or use an env file:"
    echo "  --env-file .env.docker"
    exit 1
fi

echo "✓ OpenAI API key is configured"

# Configure Codex CLI to use API key authentication
export OPENAI_API_KEY="$OPENAI_API_KEY"
echo "✓ Codex CLI configured for API key authentication"

# Check 2: Codex CLI functionality
if ! codex --version > /dev/null 2>&1; then
    echo "❌ ERROR: Codex CLI is not functional!"
    echo "Version check failed. Please ensure Codex is properly installed."
    exit 1
fi

echo "✓ Codex CLI is functional ($(codex --version))"

# Login to Codex CLI using API key
if echo "$OPENAI_API_KEY" | codex login --with-api-key > /dev/null 2>&1; then
    echo "✓ Codex CLI login successful"
else
    echo "❌ ERROR: Codex CLI login failed!"
    exit 1
fi

# Check 3: Repository path
if [ -z "$REPO_PATH" ]; then
    echo "❌ ERROR: REPO_PATH environment variable is not set!"
    exit 1
fi

if [ ! -d "$REPO_PATH" ]; then
    echo "❌ ERROR: Repository not found at: $REPO_PATH"
    echo ""
    echo "Please mount your repository:"
    echo "  -v /path/to/repo:/workspace/repo:ro"
    exit 1
fi

echo "✓ Repository found at: $REPO_PATH"

# Check 4: Git repository validation (warning only)
if [ ! -d "$REPO_PATH/.git" ]; then
    echo "⚠️  WARNING: Not a Git repository (missing .git directory)"
    echo "   Some features may not work correctly."
else
    echo "✓ Valid Git repository detected"
fi

# All checks passed
echo ""
echo "✅ Environment validated successfully!"
echo "🚀 Starting PM Component Query System..."
echo ""

# Execute the command passed to the entrypoint
exec "$@"
