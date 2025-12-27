#!/bin/bash
# 1. Pull latest code
echo "Pulling latest changes..."
git fetch origin
git reset --hard origin/main
git pull origin main

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
venv/bin/pip install -e .

# 5. Database Persistence
echo "Ensuring database persistence..."
# Old database clearing removed to maintain user data and history.

# 6. Run Database Migrations
echo "Running database migrations..."
venv/bin/python3 migrate_db.py

# 6. Start the server
echo "Starting new server..."
export ENV=prod
nohup venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &

echo "Done! Backend is starting in the background."
sleep 5
tail -n 20 backend.log

