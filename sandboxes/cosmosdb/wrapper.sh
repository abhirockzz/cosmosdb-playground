#!/bin/sh
# Wrapper script to handle file inputs from Codapi temp directory
# This runs in a new ephemeral container but connects to the long-running emulator

# Connect to emulator on host machine
export COSMOS_ENDPOINT="http://cosmosdb:8081"

# Read data.json and main.sql content from /workspace
if [ -f "/workspace/data.json" ]; then
    DATA=$(cat /workspace/data.json)
else
    DATA="[]"
fi

# Check for query - Codapi uses "entry" filename from commands.json
if [ -f "/workspace/main.sql" ]; then
    QUERY=$(cat /workspace/main.sql)
else
    # Fallback: read from stdin if no file found
    QUERY="SELECT * FROM c"
fi

# Pass as arguments to the Python script
python3 /usr/local/bin/query.py --setup "$DATA" --query "$QUERY"
