#!/bin/bash
# Docker helper script for Taiga MCP Bridge

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
}

# Show usage
usage() {
    cat << EOF
Taiga MCP Bridge - Docker Helper

Usage: $0 <command> [options]

Commands:
    build       Build the Docker image
    start       Start the server with Docker Compose
    stop        Stop the server
    restart     Restart the server
    logs        Show server logs (follow mode)
    shell       Open a shell in the container
    clean       Remove containers and images
    status      Show container status
    help        Show this help message

Options:
    -d, --detach    Run in detached mode (for start)
    -f, --follow    Follow logs (for logs command)

Examples:
    $0 build                  # Build the Docker image
    $0 start                  # Start in foreground
    $0 start -d               # Start in background
    $0 logs -f                # Follow logs
    $0 status                 # Check if running

EOF
}

# Build the image
build_image() {
    print_info "Building Docker image..."
    docker build -t taiga-mcp:latest .
    print_success "Image built successfully"
}

# Start the server
start_server() {
    local detach_flag=""
    if [[ "$1" == "-d" ]] || [[ "$1" == "--detach" ]]; then
        detach_flag="-d"
    fi
    
    # Check if .env exists
    if [[ ! -f .env ]] && [[ -f .env.docker ]]; then
        print_info "No .env file found. Copying from .env.docker..."
        cp .env.docker .env
        print_info "Please edit .env with your configuration before starting"
        exit 0
    fi
    
    print_info "Starting Taiga MCP server..."
    docker-compose up $detach_flag
    
    if [[ -n "$detach_flag" ]]; then
        print_success "Server started in background"
        print_info "Access at: http://localhost:8000"
        print_info "View logs: $0 logs -f"
    fi
}

# Stop the server
stop_server() {
    print_info "Stopping Taiga MCP server..."
    docker-compose down
    print_success "Server stopped"
}

# Restart the server
restart_server() {
    print_info "Restarting Taiga MCP server..."
    docker-compose restart
    print_success "Server restarted"
}

# Show logs
show_logs() {
    local follow_flag=""
    if [[ "$1" == "-f" ]] || [[ "$1" == "--follow" ]]; then
        follow_flag="-f"
    fi
    
    docker-compose logs $follow_flag taiga-mcp
}

# Open shell
open_shell() {
    print_info "Opening shell in container..."
    docker-compose exec taiga-mcp /bin/bash
}

# Clean up
clean_up() {
    print_info "Cleaning up containers and images..."
    docker-compose down -v
    docker rmi taiga-mcp:latest 2>/dev/null || true
    print_success "Cleanup complete"
}

# Show status
show_status() {
    echo "=== Container Status ==="
    docker-compose ps
    echo ""
    echo "=== Recent Logs ==="
    docker-compose logs --tail=20 taiga-mcp
}

# Main script
main() {
    check_docker
    
    case "${1:-help}" in
        build)
            build_image
            ;;
        start)
            start_server "$2"
            ;;
        stop)
            stop_server
            ;;
        restart)
            restart_server
            ;;
        logs)
            show_logs "$2"
            ;;
        shell)
            open_shell
            ;;
        clean)
            clean_up
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            print_error "Unknown command: $1"
            usage
            exit 1
            ;;
    esac
}

main "$@"
