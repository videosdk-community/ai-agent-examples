FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Copy the entire application to find all requirements files
COPY . .

# Install Python dependencies from all requirements.txt files
RUN echo "Installing dependencies from all requirements.txt files..." && \
    find . -name "requirements.txt" -type f | while read file; do \
        echo "Installing from: $file" && \
        pip install --no-cache-dir -r "$file"; \
    done

# Create a more flexible entrypoint script that auto-detects agents
RUN echo '#!/bin/bash\n\
\n\
# Function to find all Python files that could be agents\n\
find_agents() {\n\
    local agents=()\n\
    \n\
    # Check root level agent files\n\
    for file in *.py; do\n\
        if [[ -f "$file" && "$file" != "__init__.py" ]]; then\n\
            local name="${file%.py}"\n\
            agents+=("$name")\n\
        fi\n\
    done\n\
    \n\
    # Check basicAgents directory\n\
    if [[ -d "basicAgents" ]]; then\n\
        for file in basicAgents/*.py; do\n\
            if [[ -f "$file" && "$file" != "basicAgents/__init__.py" ]]; then\n\
                local name="${file#basicAgents/}"\n\
                name="${name%.py}"\n\
                agents+=("$name")\n\
            fi\n\
        done\n\
    fi\n\
    \n\
    # Check other directories for agents\n\
    for dir in */; do\n\
        if [[ -d "$dir" && "$dir" != "venv/" && "$dir" != "__pycache__/" ]]; then\n\
            for file in "$dir"*.py; do\n\
                if [[ -f "$file" && "$file" != "$dir"__init__.py ]]; then\n\
                    local name="${file#$dir}"\n\
                    name="${name%.py}"\n\
                    agents+=("$name")\n\
                fi\n\
            done\n\
        fi\n\
    done\n\
    \n\
    printf "%s\n" "${agents[@]}" | sort -u\n\
}\n\
\n\
# Function to run an agent\n\
run_agent() {\n\
    local agent_name=$1\n\
    \n\
    # Check if it exists in root directory\n\
    if [[ -f "${agent_name}.py" ]]; then\n\
        echo "Starting ${agent_name} agent..."\n\
        python "${agent_name}.py"\n\
        return 0\n\
    fi\n\
    \n\
    # Check if it exists in basicAgents directory\n\
    if [[ -f "basicAgents/${agent_name}.py" ]]; then\n\
        echo "Starting ${agent_name} agent..."\n\
        python "basicAgents/${agent_name}.py"\n\
        return 0\n\
    fi\n\
    \n\
    # Check other directories\n\
    for dir in */; do\n\
        if [[ -d "$dir" && "$dir" != "venv/" && "$dir" != "__pycache__/" ]]; then\n\
            if [[ -f "${dir}${agent_name}.py" ]]; then\n\
                echo "Starting ${agent_name} agent..."\n\
                python "${dir}${agent_name}.py"\n\
                return 0\n\
            fi\n\
        fi\n\
    done\n\
    \n\
    echo "Agent \"${agent_name}\" not found!"\n\
    return 1\n\
}\n\
\n\
# Function to show available agents\n\
show_agents() {\n\
    echo "Available agents:"\n\
    local agents=($(find_agents))\n\
    \n\
    if [[ ${#agents[@]} -eq 0 ]]; then\n\
        echo "  No agents found!"\n\
        return\n\
    fi\n\
    \n\
    for agent in "${agents[@]}"; do\n\
        echo "  $agent"\n\
    done\n\
    \n\
    echo ""\n\
    echo "Usage: docker run --env-file .env ai-agent-examples <agent_name>"\n\
    echo "Example: docker run --env-file .env ai-agent-examples celebrity"\n\
}\n\
\n\
# Main logic\n\
case "${1:-}" in\n\
    "list"|"")\n\
        show_agents\n\
        ;;\n\
    *)\n\
        run_agent "$1"\n\
        ;;\n\
esac' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"] 