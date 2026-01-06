#!/bin/bash

# Ensure we are in the project root
cd "$(dirname "$0")/.."

COMMIT_MSG=$1

if [ -z "$COMMIT_MSG" ]; then
    echo "Error: No commit message provided."
    echo "Usage: ./scripts/safe_commit.sh \"your commit message\""
    exit 1
fi

echo "Running full test suite..."

# Run tests using the virtual environment's pytest
if [ -f "./venv/bin/pytest" ]; then
    ./venv/bin/pytest
else
    echo "Error: Virtual environment pytest not found at ./venv/bin/pytest"
    exit 1
fi

# Check exit code of pytest
if [ $? -eq 0 ]; then
    echo "Tests passed! Committing changes..."
    git add .
    git commit -m "$COMMIT_MSG"
else
    echo "Tests failed. Commit aborted."
    exit 1
fi