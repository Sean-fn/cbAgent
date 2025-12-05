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

# Check 4: Update all git repositories in /workspace/repo
echo ""
echo "🔄 Updating git repositories..."

# Function to update a single repository
update_repo() {
    local repo_path="$1"
    local repo_name=$(basename "$repo_path")

    echo "  📦 Updating: $repo_name"

    cd "$repo_path" || return 1

    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        echo "    ⚠️  Skipping: uncommitted changes detected"
        return 0
    fi

    # Attempt to pull
    if git pull --ff-only 2>&1 | sed 's/^/    /'; then
        echo "    ✓ Updated successfully"
    else
        echo "    ⚠️  Update failed (may need manual intervention)"
    fi
}

# Find and update all git repositories
repo_count=0

# Check if /workspace/repo itself is a git repository
if [ -d "$REPO_PATH/.git" ]; then
    update_repo "$REPO_PATH"
    repo_count=$((repo_count + 1))
fi

# Find all subdirectories containing .git
while IFS= read -r git_dir; do
    repo_dir=$(dirname "$git_dir")
    update_repo "$repo_dir"
    repo_count=$((repo_count + 1))
done < <(find "$REPO_PATH" -mindepth 2 -maxdepth 2 -type d -name ".git" 2>/dev/null)

if [ $repo_count -eq 0 ]; then
    echo "  ⚠️  No git repositories found in $REPO_PATH"
else
    echo "  ✓ Processed $repo_count repository/repositories"
fi

# All checks passed
echo ""
echo "✅ Environment validated successfully!"
echo "🚀 Starting PM Component Query System..."
echo ""

# Execute the command passed to the entrypoint
exec "$@"
