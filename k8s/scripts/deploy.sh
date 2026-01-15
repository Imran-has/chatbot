#!/bin/bash
# Deploy Todo Chatbot to Minikube using Helm
# This script handles the complete deployment process

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELM_CHART_DIR="$SCRIPT_DIR/../helm/todo-chatbot"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
RELEASE_NAME="${RELEASE_NAME:-todo-chatbot}"
NAMESPACE="${NAMESPACE:-todo-chatbot}"
OPENAI_API_KEY="${OPENAI_API_KEY:-}"
VALUES_FILE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --release-name)
            RELEASE_NAME="$2"
            shift 2
            ;;
        --namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        --openai-key)
            OPENAI_API_KEY="$2"
            shift 2
            ;;
        --values)
            VALUES_FILE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --release-name NAME   Helm release name (default: todo-chatbot)"
            echo "  --namespace NS        Kubernetes namespace (default: todo-chatbot)"
            echo "  --openai-key KEY      OpenAI API key (required)"
            echo "  --values FILE         Additional values file"
            echo "  -h, --help            Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  Deploying Todo Chatbot to Kubernetes${NC}"
echo -e "${GREEN}======================================${NC}"

# Check prerequisites
echo -e "\n${BLUE}Checking prerequisites...${NC}"

# Check Minikube
if ! command -v minikube &> /dev/null; then
    echo -e "${RED}Error: Minikube is not installed.${NC}"
    exit 1
fi

# Check if Minikube is running
if ! minikube status | grep -q "Running"; then
    echo -e "${YELLOW}Starting Minikube...${NC}"
    minikube start
fi
echo -e "${GREEN}✓ Minikube is running${NC}"

# Check Helm
if ! command -v helm &> /dev/null; then
    echo -e "${RED}Error: Helm is not installed.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Helm is installed${NC}"

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ kubectl is installed${NC}"

# Check OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}Warning: OPENAI_API_KEY is not set. The chatbot AI features will not work.${NC}"
    echo -e "${YELLOW}You can set it with: export OPENAI_API_KEY=your-key${NC}"
fi

# Configure Docker to use Minikube's daemon
echo -e "\n${BLUE}Configuring Docker for Minikube...${NC}"
eval $(minikube docker-env)

# Build images
echo -e "\n${BLUE}Building Docker images...${NC}"
"$SCRIPT_DIR/build-images.sh"

# Create namespace if it doesn't exist
echo -e "\n${BLUE}Creating namespace '$NAMESPACE'...${NC}"
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Add Bitnami repo for PostgreSQL dependency
echo -e "\n${BLUE}Adding Helm repositories...${NC}"
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Update dependencies
echo -e "\n${BLUE}Updating Helm dependencies...${NC}"
helm dependency update "$HELM_CHART_DIR"

# Deploy with Helm
echo -e "\n${BLUE}Deploying with Helm...${NC}"

HELM_ARGS=(
    upgrade --install "$RELEASE_NAME" "$HELM_CHART_DIR"
    --namespace "$NAMESPACE"
    --set "secrets.openaiApiKey=$OPENAI_API_KEY"
    --set "backend.image.pullPolicy=Never"
    --set "frontend.image.pullPolicy=Never"
)

if [ -n "$VALUES_FILE" ]; then
    HELM_ARGS+=(-f "$VALUES_FILE")
fi

helm "${HELM_ARGS[@]}"

# Wait for deployment
echo -e "\n${BLUE}Waiting for deployments to be ready...${NC}"
kubectl rollout status deployment/"$RELEASE_NAME-todo-chatbot-backend" -n "$NAMESPACE" --timeout=300s || true
kubectl rollout status deployment/"$RELEASE_NAME-todo-chatbot-frontend" -n "$NAMESPACE" --timeout=300s || true

# Get status
echo -e "\n${GREEN}======================================${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${GREEN}======================================${NC}"

echo -e "\n${BLUE}Pod Status:${NC}"
kubectl get pods -n "$NAMESPACE"

echo -e "\n${BLUE}Service Status:${NC}"
kubectl get services -n "$NAMESPACE"

# Get access URL
echo -e "\n${BLUE}Access Information:${NC}"
FRONTEND_URL=$(minikube service "$RELEASE_NAME-todo-chatbot-frontend" -n "$NAMESPACE" --url 2>/dev/null || echo "pending")
echo -e "${GREEN}Frontend URL: $FRONTEND_URL${NC}"

echo -e "\n${YELLOW}To access the application, run:${NC}"
echo -e "minikube service $RELEASE_NAME-todo-chatbot-frontend -n $NAMESPACE"
