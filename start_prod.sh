#!/bin/bash
# 1. Pull latest code
echo "Pulling latest changes..."
git fetch origin
git reset --hard origin/main
git clean -fd
git pull origin main

# 2. Ensure Virtual Environment exists
if [ ! -d "venv/bin" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 3. Kill existing uvicorn processes
echo "Stopping old server..."
pkill uvicorn || echo "No uvicorn process was running."

# 4. Check if requirements changed
REQ_HASH_FILE="venv/.requirements_hash"
CURRENT_HASH=$(md5sum requirements.txt | awk '{print $1}')
STORED_HASH=""
if [ -f "$REQ_HASH_FILE" ]; then
    STORED_HASH=$(cat "$REQ_HASH_FILE")
fi

if [ "$CURRENT_HASH" != "$STORED_HASH" ]; then
    echo "Requirements changed. Updating dependencies..."
    # Use 'nice' to prevent locking up the CPU
    # Use --no-cache-dir to save memory on small instances
    nice -n 10 venv/bin/pip install --no-cache-dir -r requirements.txt
    echo "$CURRENT_HASH" > "$REQ_HASH_FILE"
else
    echo "Requirements unchanged. Skipping pip install."
fi

# Always install local package in editable mode (fast)
venv/bin/pip install -e .

# 5. Run Database Migrations (nice for safety)
echo "Running database migrations..."
nice -n 10 venv/bin/python3 migrate_db.py

# 6. Start the server
echo "Starting new server..."
export ENV=prod
# Run uvicorn with a slightly lower priority so SSH remains responsive
nohup nice -n 5 venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &

echo "Done! Backend is starting in the background."
sleep 2
tail -n 5 backend.log

