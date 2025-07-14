#!/bin/bash

# Lord of the Pings Development Script

echo "🚀 Starting Lord of the Pings Development Environment..."

# Check if .env file exists, if not copy from example
if [ ! -f .env ]; then
    echo "📁 Creating .env file from example..."
    cp .env.example .env
fi

# Install dependencies if requirements.txt has changed
if [ ! -f .pip_installed ] || [ requirements.txt -nt .pip_installed ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    touch .pip_installed
fi

# Initialize database
echo "🗃️ Initializing database..."
python -m db.init_db

# Start the Flask app in one terminal
echo "🌐 Starting Flask web server..."
flask run --port 5000 &
FLASK_PID=$!

# Start the agent in another terminal
echo "🤖 Starting monitoring agent..."
python agent/agent.py &
AGENT_PID=$!

# Function to cleanup on exit
cleanup() {
    echo "🧹 Cleaning up..."
    kill $FLASK_PID $AGENT_PID 2>/dev/null || true
    echo "✅ Development environment stopped."
}

# Trap signals for cleanup
trap cleanup EXIT INT TERM

echo "🎉 Development environment started!"
echo "🌐 Web interface: http://localhost:5000"
echo "🤖 Agent is running in background"
echo "📝 Press Ctrl+C to stop"

# Wait for processes
wait $FLASK_PID $AGENT_PID
