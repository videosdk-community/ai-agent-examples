#!/bin/bash

# AI Agent Examples - Docker Runner
# This script makes it super easy to run any AI agent with Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤖 AI Agent Examples - Docker Runner${NC}"
echo "=================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo -e "${YELLOW}Please create a .env file with your API keys:${NC}"
    echo "VIDEOSDK_AUTH_TOKEN=your_videosdk_token"
    echo "OPENAI_API_KEY=your_openai_key"
    echo "GOOGLE_API_KEY=your_google_key"
    echo "AWS_ACCESS_KEY_ID=your_aws_key"
    echo "AWS_SECRET_ACCESS_KEY=your_aws_secret"
    echo "AWS_DEFAULT_REGION=your_aws_region"
    exit 1
fi

# Function to find all Python files that could be agents
find_agents() {
    local agents=()
    
    # Check root level agent files
    for file in *.py; do
        if [[ -f "$file" && "$file" != "__init__.py" ]]; then
            local name="${file%.py}"
            agents+=("$name")
        fi
    done
    
    # Check basicAgents directory
    if [[ -d "basicAgents" ]]; then
        for file in basicAgents/*.py; do
            if [[ -f "$file" && "$file" != "basicAgents/__init__.py" ]]; then
                local name="${file#basicAgents/}"
                name="${name%.py}"
                agents+=("$name")
            fi
        done
    fi
    
    # Check other directories for agents
    for dir in */; do
        if [[ -d "$dir" && "$dir" != "venv/" && "$dir" != "__pycache__/" ]]; then
            for file in "$dir"*.py; do
                if [[ -f "$file" && "$file" != "$dir"__init__.py ]]; then
                    local name="${file#$dir}"
                    name="${name%.py}"
                    agents+=("$name")
                fi
            done
        fi
    done
    
    printf "%s\n" "${agents[@]}" | sort -u
}

# Function to show available agents
show_agents() {
    echo -e "${GREEN}Available agents:${NC}"
    local agents=($(find_agents))
    
    if [[ ${#agents[@]} -eq 0 ]]; then
        echo "  No agents found!"
        return
    fi
    
    for agent in "${agents[@]}"; do
        echo "  $agent"
    done
    
    echo ""
    echo -e "${YELLOW}Usage: ./run.sh <agent_name>${NC}"
    echo -e "${YELLOW}Example: ./run.sh celebrity${NC}"
}

# Function to build the Docker image
build_image() {
    echo -e "${BLUE}🔨 Building Docker image...${NC}"
    docker build -t ai-agent-examples .
    echo -e "${GREEN}✅ Docker image built successfully!${NC}"
}

# Function to run an agent
run_agent() {
    local agent=$1
    echo -e "${GREEN}🚀 Starting $agent agent...${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop the agent${NC}"
    echo ""
    
    docker run --rm -it \
        --env-file .env \
        -e PYTHONUNBUFFERED=1 \
        ai-agent-examples "$agent"
}

# Function to check if agent exists
agent_exists() {
    local agent=$1
    local agents=($(find_agents))
    
    for existing_agent in "${agents[@]}"; do
        if [[ "$existing_agent" == "$agent" ]]; then
            return 0
        fi
    done
    return 1
}

# Main logic
case "${1:-}" in
    "build")
        build_image
        ;;
    "list"|"")
        show_agents
        ;;
    *)
        if agent_exists "$1"; then
            # Check if image exists, build if not
            if ! docker image inspect ai-agent-examples >/dev/null 2>&1; then
                echo -e "${YELLOW}⚠️  Docker image not found. Building...${NC}"
                build_image
            fi
            run_agent "$1"
        else
            echo -e "${RED}❌ Unknown agent: $1${NC}"
            echo ""
            show_agents
            exit 1
        fi
        ;;
esac 