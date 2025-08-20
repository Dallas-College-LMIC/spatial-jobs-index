#!/usr/bin/env bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is already running
check_backend() {
    if lsof -i:8000 >/dev/null 2>&1; then
        echo -e "${YELLOW}Backend is already running on port 8000${NC}"
        return 0
    else
        return 1
    fi
}

# Check if frontend is already running
check_frontend() {
    if lsof -i:3000 >/dev/null 2>&1; then
        echo -e "${YELLOW}Frontend is already running on port 3000${NC}"
        return 0
    else
        return 1
    fi
}

# Get project root directory (parent of tools)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Start backend if not running
if ! check_backend; then
    echo -e "${GREEN}Starting backend...${NC}"
    cd "$PROJECT_ROOT/backend" && nohup uv run python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > "$PROJECT_ROOT/backend.log" 2>&1 &
    echo $! > "$PROJECT_ROOT/backend.pid"
    echo -e "${GREEN}Backend started (PID: $(cat "$PROJECT_ROOT/backend.pid"))${NC}"
fi

# Start frontend if not running
if ! check_frontend; then
    echo -e "${GREEN}Starting frontend...${NC}"
    cd "$PROJECT_ROOT/frontend" && nohup npm run dev > "$PROJECT_ROOT/frontend.log" 2>&1 &
    echo $! > "$PROJECT_ROOT/frontend.pid"
    echo -e "${GREEN}Frontend started (PID: $(cat "$PROJECT_ROOT/frontend.pid"))${NC}"
fi

echo -e "\n${GREEN}Development servers status:${NC}"
echo -e "Backend: http://localhost:8000"
echo -e "Frontend: http://localhost:3000"
echo -e "\nLogs available at:"
echo -e "  backend.log"
echo -e "  frontend.log"
echo -e "\nTo stop servers, run: just stop"
