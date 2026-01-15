#!/bin/bash
# Build Docker images for Todo Chatbot application
# This script builds both frontend and backend images for local Kubernetes deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  Building Todo Chatbot Docker Images${NC}"
echo -e "${GREEN}======================================${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi

# Check if using Minikube's Docker daemon
if command -v minikube &> /dev/null; then
    echo -e "${YELLOW}Configuring to use Minikube's Docker daemon...${NC}"
    eval $(minikube docker-env)
    echo -e "${GREEN}Using Minikube's Docker daemon${NC}"
fi

# Build backend image
echo -e "\n${YELLOW}Building backend image...${NC}"
docker build -t todo-chatbot-backend:latest "$PROJECT_ROOT/backend"
echo -e "${GREEN}Backend image built successfully!${NC}"

# Build frontend image
echo -e "\n${YELLOW}Building frontend image...${NC}"
docker build -t todo-chatbot-frontend:latest "$PROJECT_ROOT/frontend"
echo -e "${GREEN}Frontend image built successfully!${NC}"

# List built images
echo -e "\n${GREEN}======================================${NC}"
echo -e "${GREEN}  Built Images:${NC}"
echo -e "${GREEN}======================================${NC}"
docker images | grep -E "todo-chatbot-(backend|frontend)"

echo -e "\n${GREEN}All images built successfully!${NC}"
echo -e "${YELLOW}Note: If using Minikube, images are now available in Minikube's registry.${NC}"
