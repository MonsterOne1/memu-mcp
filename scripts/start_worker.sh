#!/bin/bash

# memU MCP Server Worker Startup Script for Render
# This script handles the startup and monitoring of the MCP worker process

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="${PROJECT_ROOT}/logs/worker.log"
PID_FILE="${PROJECT_ROOT}/worker.pid"
MAX_RESTARTS="${MAX_RETRY_ATTEMPTS:-3}"
RESTART_DELAY="${WORKER_RESTART_DELAY:-5}"

# Ensure logs directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Logging functions
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "$LOG_FILE" >&2
}

log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $*" | tee -a "$LOG_FILE"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up worker process..."
    if [[ -f "$PID_FILE" ]]; then
        local pid
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log_info "Killing worker process $pid"
            kill -TERM "$pid" 2>/dev/null || true
            sleep 2
            kill -KILL "$pid" 2>/dev/null || true
        fi
        rm -f "$PID_FILE"
    fi
}

# Trap signals for cleanup
trap cleanup EXIT INT TERM

# Check required environment variables
check_environment() {
    log_info "Checking environment variables..."
    
    if [[ -z "${MEMU_API_KEY:-}" ]]; then
        log_error "MEMU_API_KEY environment variable is required"
        exit 1
    fi
    
    if [[ -z "${RENDER_DEPLOYMENT:-}" ]]; then
        log_info "Not running in Render environment"
    else
        log_info "Running in Render environment"
    fi
    
    log_info "Environment check passed"
}

# Start the MCP worker process
start_worker() {
    log_info "Starting memU MCP worker..."
    
    cd "$PROJECT_ROOT"
    
    # Set Python path
    export PYTHONPATH="${PROJECT_ROOT}/src:${PYTHONPATH:-}"
    
    # Start the worker process
    python -m memu_mcp_server.main --render-mode &
    local worker_pid=$!
    
    # Save PID
    echo "$worker_pid" > "$PID_FILE"
    log_info "Worker started with PID $worker_pid"
    
    return "$worker_pid"
}

# Monitor worker process
monitor_worker() {
    local worker_pid=$1
    local restart_count=0
    
    log_info "Monitoring worker process $worker_pid"
    
    while true; do
        if ! kill -0 "$worker_pid" 2>/dev/null; then
            log_error "Worker process $worker_pid has died"
            
            if [[ $restart_count -ge $MAX_RESTARTS ]]; then
                log_error "Maximum restart attempts ($MAX_RESTARTS) reached. Exiting."
                exit 1
            fi
            
            restart_count=$((restart_count + 1))
            log_info "Restarting worker (attempt $restart_count/$MAX_RESTARTS)..."
            
            # Wait before restarting
            sleep "$RESTART_DELAY"
            
            # Start new worker
            start_worker
            worker_pid=$!
            
            log_info "Worker restarted with new PID $worker_pid"
        fi
        
        # Check every 10 seconds
        sleep 10
    done
}

# Health check function
health_check() {
    log_info "Performing health check..."
    
    # Check if PID file exists and process is running
    if [[ -f "$PID_FILE" ]]; then
        local pid
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log_info "Worker process $pid is running"
            return 0
        else
            log_error "Worker process $pid is not running"
            return 1
        fi
    else
        log_error "PID file not found"
        return 1
    fi
}

# Status function
status() {
    if [[ -f "$PID_FILE" ]]; then
        local pid
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo "Worker is running (PID: $pid)"
            return 0
        else
            echo "Worker is not running (stale PID file)"
            return 1
        fi
    else
        echo "Worker is not running"
        return 1
    fi
}

# Stop function
stop_worker() {
    log_info "Stopping memU MCP worker..."
    cleanup
    log_info "Worker stopped"
}

# Main function
main() {
    case "${1:-start}" in
        start)
            log_info "Starting memU MCP Server Worker"
            check_environment
            
            # Check if already running
            if [[ -f "$PID_FILE" ]]; then
                local existing_pid
                existing_pid=$(cat "$PID_FILE")
                if kill -0 "$existing_pid" 2>/dev/null; then
                    log_error "Worker is already running with PID $existing_pid"
                    exit 1
                else
                    log_info "Removing stale PID file"
                    rm -f "$PID_FILE"
                fi
            fi
            
            # Start worker
            start_worker
            local worker_pid=$!
            
            # Monitor the process
            monitor_worker "$worker_pid"
            ;;
            
        stop)
            stop_worker
            ;;
            
        restart)
            stop_worker
            sleep 2
            main start
            ;;
            
        status)
            status
            ;;
            
        health)
            health_check
            ;;
            
        *)
            echo "Usage: $0 {start|stop|restart|status|health}"
            echo ""
            echo "Commands:"
            echo "  start   - Start the worker process"
            echo "  stop    - Stop the worker process"
            echo "  restart - Restart the worker process"
            echo "  status  - Show worker status"
            echo "  health  - Perform health check"
            exit 1
            ;;
    esac
}

# Set up signal handlers
trap 'log_info "Received SIGTERM, shutting down..."; cleanup; exit 0' TERM
trap 'log_info "Received SIGINT, shutting down..."; cleanup; exit 0' INT

# Run main function
main "$@"