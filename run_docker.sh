# Usage: ./run.sh /path/to/repositories

export HOST_REPO_PATH=$1
echo "🔄 Updating git repositories in $HOST_REPO_PATH ..."
if [ -d "$HOST_REPO_PATH/.git" ]; then
    echo "Pulling in $HOST_REPO_PATH"
    if (cd "$HOST_REPO_PATH" && git pull); then
        echo "✓ Successfully pulled $HOST_REPO_PATH"
    else
        echo "✗ Failed to pull $HOST_REPO_PATH"
    fi
else
    for dir in "$HOST_REPO_PATH"/*/; do
        if [ -d "$dir/.git" ]; then
            echo "Pulling in $dir"
            if (cd "$dir" && git pull); then
                echo "✓ Successfully pulled $dir"
            else
                echo "✗ Failed to pull $dir"
            fi
        fi
    done
fi


# docker-compose run --rm cb-agent-system
docker run -it --rm --env-file .env.docker -v $HOST_REPO_PATH:/workspace/repo --name cb-agent docker.io/seanfn/cb-agent-system:latest python -m src.main