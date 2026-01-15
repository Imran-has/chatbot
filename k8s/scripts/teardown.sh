#!/bin/bash
# Teardown Todo Chatbot deployment from Kubernetes
# This script removes all resources created by the Helm chart

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
RELEASE_NAME="${RELEASE_NAME:-todo-chatbot}"
NAMESPACE="${NAMESPACE:-todo-chatbot}"
DELETE_NAMESPACE="${DELETE_NAMESPACE:-false}"
DELETE_PVC="${DELETE_PVC:-false}"

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
        --delete-namespace)
            DELETE_NAMESPACE="true"
            shift
            ;;
        --delete-pvc)
            DELETE_PVC="true"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --release-name NAME   Helm release name (default: todo-chatbot)"
            echo "  --namespace NS        Kubernetes namespace (default: todo-chatbot)"
            echo "  --delete-namespace    Also delete the namespace"
            echo "  --delete-pvc          Also delete persistent volume claims (data will be lost)"
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
echo -e "${GREEN}  Tearing Down Todo Chatbot${NC}"
echo -e "${GREEN}======================================${NC}"

echo -e "\n${YELLOW}Release: $RELEASE_NAME${NC}"
echo -e "${YELLOW}Namespace: $NAMESPACE${NC}"

# Uninstall Helm release
echo -e "\n${BLUE}Uninstalling Helm release...${NC}"
if helm status "$RELEASE_NAME" -n "$NAMESPACE" > /dev/null 2>&1; then
    helm uninstall "$RELEASE_NAME" -n "$NAMESPACE"
    echo -e "${GREEN}✓ Helm release uninstalled${NC}"
else
    echo -e "${YELLOW}Release '$RELEASE_NAME' not found in namespace '$NAMESPACE'${NC}"
fi

# Delete PVCs if requested
if [ "$DELETE_PVC" = "true" ]; then
    echo -e "\n${BLUE}Deleting Persistent Volume Claims...${NC}"
    kubectl delete pvc --all -n "$NAMESPACE" --ignore-not-found
    echo -e "${GREEN}✓ PVCs deleted${NC}"
fi

# Delete namespace if requested
if [ "$DELETE_NAMESPACE" = "true" ]; then
    echo -e "\n${BLUE}Deleting namespace...${NC}"
    kubectl delete namespace "$NAMESPACE" --ignore-not-found
    echo -e "${GREEN}✓ Namespace deleted${NC}"
fi

echo -e "\n${GREEN}======================================${NC}"
echo -e "${GREEN}  Teardown Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
