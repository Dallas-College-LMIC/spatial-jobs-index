mod frontend
mod backend

# Run both frontend and backend development servers
start:
    @./tools/run-dev.sh

# Stop both frontend and backend development servers
stop:
    @./tools/stop-dev.sh
