#!/usr/bin/env bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get project root directory (parent of tools)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Function to kill process and its children
kill_process_tree() {
    local pid=$1
    local child_pids=$(pgrep -P $pid 2>/dev/null)

    # Kill children first
    for child in $child_pids; do
        kill_process_tree $child
    done

    # Then kill the parent
    kill $pid 2>/dev/null
}

# Stop backend
backend_stopped=false
if [ -f "$PROJECT_ROOT/backend.pid" ]; then
    PID=$(cat "$PROJECT_ROOT/backend.pid")
    if kill -0 $PID 2>/dev/null; then
        echo -e "${YELLOW}Stopping backend (PID: $PID and children)...${NC}"
        kill_process_tree $PID
        rm "$PROJECT_ROOT/backend.pid"
        backend_stopped=true
        echo -e "${GREEN}Backend stopped${NC}"
    else
        echo -e "${YELLOW}Backend process not found, cleaning up PID file${NC}"
        rm "$PROJECT_ROOT/backend.pid"
    fi
fi

# Also kill any uvicorn processes on port 8000
if ! $backend_stopped && lsof -i:8000 >/dev/null 2>&1; then
    echo -e "${YELLOW}Stopping backend processes on port 8000...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    echo -e "${GREEN}Backend stopped${NC}"
elif ! $backend_stopped; then
    echo -e "${YELLOW}Backend is not running${NC}"
fi

# Stop frontend
frontend_stopped=false
if [ -f "$PROJECT_ROOT/frontend.pid" ]; then
    PID=$(cat "$PROJECT_ROOT/frontend.pid")
    if kill -0 $PID 2>/dev/null; then
        echo -e "${YELLOW}Stopping frontend (PID: $PID and children)...${NC}"
        kill_process_tree $PID
        rm "$PROJECT_ROOT/frontend.pid"
        frontend_stopped=true
        echo -e "${GREEN}Frontend stopped${NC}"
    else
        echo -e "${YELLOW}Frontend process not found, cleaning up PID file${NC}"
        rm "$PROJECT_ROOT/frontend.pid"
    fi
fi

# Also kill any vite/node processes on port 3000
if ! $frontend_stopped && lsof -i:3000 >/dev/null 2>&1; then
    echo -e "${YELLOW}Stopping frontend processes on port 3000...${NC}"
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    echo -e "${GREEN}Frontend stopped${NC}"
elif ! $frontend_stopped; then
    echo -e "${YELLOW}Frontend is not running${NC}"
fi

echo -e "\n${GREEN}All development servers stopped${NC}"
