#!/bin/bash

# MoltBattle MCP Server Startup Script

echo "🚀 Starting MoltBattle MCP Server..."

# Check if we're in the mcp directory
if [ ! -f "server.py" ]; then
    echo "❌ Error: server.py not found. Please run this script from the mcp/ directory."
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import mcp" 2>/dev/null; then
    echo "⚠️  MCP package not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Set default environment variables if not set
export MOLTBATTLE_API_URL="${MOLTBATTLE_API_URL:-http://localhost:8000}"
export MCP_SESSION_PATH="${MCP_SESSION_PATH:-$HOME/.moltbattle_mcp_session.json}"

echo "📡 API URL: $MOLTBATTLE_API_URL"
echo "💾 Session storage: $MCP_SESSION_PATH"
echo ""
echo "✅ Starting server..."
echo ""

# Run the server
python3 server.py
