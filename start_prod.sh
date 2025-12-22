#!/bin/bash
# 1. Pull latest code
echo "Pulling latest changes..."
git pull

# 2. Ensure Virtual Environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    sudo apt update && sudo apt install -y python3-venv
    python3 -m venv venv
fi

# 3. Kill existing uvicorn processes
echo "Stopping old server..."
pkill uvicorn || echo "No uvicorn process was running."

# 4. Ensure dependencies are up to date
echo "Updating dependencies..."
venv/bin/pip install -r requirements.txt

# 5. Start the server
echo "Starting new server..."
nohup venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &

echo "Done! Backend is running in the background."
sleep 2
tail -n 10 backend.log
