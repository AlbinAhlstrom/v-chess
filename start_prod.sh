#!/bin/bash
# 1. Pull latest code
echo "Pulling latest changes..."
git pull

# 2. Kill existing uvicorn processes
echo "Stopping old server..."
pkill uvicorn || echo "No uvicorn process was running."

# 3. Ensure dependencies are up to date
echo "Updating dependencies..."
venv/bin/pip install -r requirements.txt

# 4. Start the server
echo "Starting new server..."
nohup venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &

echo "Done! Backend is running in the background."
tail -n 5 backend.log