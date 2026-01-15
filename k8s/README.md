# Phase IV: Local Kubernetes Deployment

Deploy the Todo Chatbot application on a local Kubernetes cluster using Minikube and Helm Charts.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Minikube Cluster                                │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        Namespace: todo-chatbot                         │  │
│  │                                                                        │  │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │  │
│  │  │    Frontend     │    │     Backend     │    │   PostgreSQL    │   │  │
│  │  │    (Next.js)    │───▶│    (FastAPI)    │───▶│    Database     │   │  │
│  │  │   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │   │  │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘   │  │
│  │         │                       │                      │              │  │
│  │         ▼                       ▼                      ▼              │  │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │  │
│  │  │ NodePort:30000  │    │   ClusterIP     │    │     PVC         │   │  │
│  │  │    Service      │    │    Service      │    │   (1Gi Data)    │   │  │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘   │  │
│  │                                                                        │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

### Required Software

| Tool | Version | Purpose |
|------|---------|---------|
| Docker Desktop | 4.53+ | Container runtime |
| Minikube | Latest | Local Kubernetes cluster |
| Helm | 3.x | Kubernetes package manager |
| kubectl | Latest | Kubernetes CLI |

### Optional AI Tools

| Tool | Purpose |
|------|---------|
| Docker AI (Gordon) | AI-assisted Docker operations |
| kubectl-ai | AI-assisted Kubernetes operations |
| Kagent | Advanced Kubernetes AI operations |

## Quick Start

### 1. Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Verify Minikube is running
minikube status
```

### 2. Configure Docker for Minikube

```bash
# Point Docker to Minikube's daemon
eval $(minikube docker-env)
```

### 3. Build Docker Images

```bash
# Navigate to the project directory
cd /path/to/chatbot

# Build images using the script
./k8s/scripts/build-images.sh

# Or build manually:
docker build -t todo-chatbot-backend:latest ./backend
docker build -t todo-chatbot-frontend:latest ./frontend
```

### 4. Deploy with Helm

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-openai-api-key"

# Deploy using the script
./k8s/scripts/deploy.sh --openai-key "$OPENAI_API_KEY"

# Or deploy manually:
helm dependency update ./k8s/helm/todo-chatbot
helm install todo-chatbot ./k8s/helm/todo-chatbot \
  --namespace todo-chatbot \
  --create-namespace \
  --set secrets.openaiApiKey="$OPENAI_API_KEY" \
  --set backend.image.pullPolicy=Never \
  --set frontend.image.pullPolicy=Never
```

### 5. Access the Application

```bash
# Get the frontend URL
minikube service todo-chatbot-todo-chatbot-frontend -n todo-chatbot --url

# Or use port-forwarding:
kubectl port-forward svc/todo-chatbot-todo-chatbot-frontend 3000:3000 -n todo-chatbot
```

## Using Docker AI Agent (Gordon)

If Docker Desktop 4.53+ with Gordon enabled:

```bash
# Get Docker AI capabilities
docker ai "What can you do?"

# Build images with AI assistance
docker ai "build the backend Dockerfile in ./backend"
docker ai "build the frontend Dockerfile in ./frontend"

# Analyze and optimize Dockerfiles
docker ai "analyze the Dockerfile in ./backend for best practices"
```

## Using kubectl-ai

```bash
# Deploy with AI assistance
kubectl-ai "deploy the todo frontend with 2 replicas"
kubectl-ai "scale the backend to handle more load"
kubectl-ai "check why the pods are failing"

# Debug issues
kubectl-ai "show me the logs for the failing backend pod"
kubectl-ai "describe the todo-chatbot-backend deployment"
```

## Using Kagent

```bash
# Cluster health analysis
kagent "analyze the cluster health"

# Resource optimization
kagent "optimize resource allocation for todo-chatbot namespace"

# Troubleshooting
kagent "diagnose issues with the todo-chatbot deployment"
```

## Helm Chart Configuration

### Default Values

The chart uses these default configurations:

| Component | Setting | Default Value |
|-----------|---------|---------------|
| Backend | replicas | 1 |
| Backend | port | 8000 |
| Backend | resources.cpu | 100m-500m |
| Backend | resources.memory | 256Mi-512Mi |
| Frontend | replicas | 1 |
| Frontend | port | 3000 |
| Frontend | nodePort | 30000 |
| PostgreSQL | enabled | true |
| PostgreSQL | storage | 1Gi |

### Custom Values

Create a `custom-values.yaml`:

```yaml
# Increase replicas for production
backend:
  replicaCount: 2
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5

frontend:
  replicaCount: 2

# Use external database
postgresql:
  enabled: false
secrets:
  databaseUrl: "postgresql+asyncpg://user:pass@host:5432/db"
```

Deploy with custom values:

```bash
helm install todo-chatbot ./k8s/helm/todo-chatbot \
  -f custom-values.yaml \
  --set secrets.openaiApiKey="$OPENAI_API_KEY"
```

## Directory Structure

```
k8s/
├── helm/
│   └── todo-chatbot/
│       ├── Chart.yaml              # Chart metadata
│       ├── values.yaml             # Default configuration
│       ├── .helmignore             # Files to ignore
│       └── templates/
│           ├── _helpers.tpl        # Template helpers
│           ├── namespace.yaml      # Namespace definition
│           ├── serviceaccount.yaml # Service account
│           ├── configmap.yaml      # Configuration
│           ├── secret.yaml         # Secrets
│           ├── backend-deployment.yaml
│           ├── backend-service.yaml
│           ├── backend-hpa.yaml
│           ├── frontend-deployment.yaml
│           ├── frontend-service.yaml
│           ├── frontend-hpa.yaml
│           ├── database-deployment.yaml
│           ├── database-service.yaml
│           ├── database-pvc.yaml
│           ├── ingress.yaml
│           └── NOTES.txt           # Post-install notes
├── scripts/
│   ├── build-images.sh             # Build Docker images
│   ├── deploy.sh                   # Deploy to Minikube
│   └── teardown.sh                 # Remove deployment
└── README.md                       # This file
```

## Common Operations

### Check Deployment Status

```bash
# View all resources
kubectl get all -n todo-chatbot

# Check pod status
kubectl get pods -n todo-chatbot

# View pod logs
kubectl logs -f deployment/todo-chatbot-todo-chatbot-backend -n todo-chatbot
kubectl logs -f deployment/todo-chatbot-todo-chatbot-frontend -n todo-chatbot
```

### Scale Deployments

```bash
# Scale backend
kubectl scale deployment todo-chatbot-todo-chatbot-backend \
  --replicas=3 -n todo-chatbot

# Or with kubectl-ai:
kubectl-ai "scale the backend deployment to 3 replicas"
```

### Update Configuration

```bash
# Update with new values
helm upgrade todo-chatbot ./k8s/helm/todo-chatbot \
  -n todo-chatbot \
  --set backend.replicaCount=2

# Rollback if needed
helm rollback todo-chatbot -n todo-chatbot
```

### Debug Issues

```bash
# Describe pods
kubectl describe pods -n todo-chatbot

# Check events
kubectl get events -n todo-chatbot --sort-by='.lastTimestamp'

# Execute into container
kubectl exec -it deployment/todo-chatbot-todo-chatbot-backend \
  -n todo-chatbot -- /bin/sh
```

## Teardown

```bash
# Remove deployment
./k8s/scripts/teardown.sh

# Or manually:
helm uninstall todo-chatbot -n todo-chatbot
kubectl delete namespace todo-chatbot

# Stop Minikube
minikube stop
```

## Troubleshooting

### Image Pull Errors

If pods show `ImagePullBackOff`:

```bash
# Ensure using Minikube's Docker daemon
eval $(minikube docker-env)

# Rebuild images
./k8s/scripts/build-images.sh

# Verify images exist
docker images | grep todo-chatbot
```

### Database Connection Issues

```bash
# Check PostgreSQL status
kubectl get pods -n todo-chatbot -l app.kubernetes.io/component=database

# View database logs
kubectl logs -f deployment/todo-chatbot-todo-chatbot-database -n todo-chatbot

# Test connectivity
kubectl exec -it deployment/todo-chatbot-todo-chatbot-backend \
  -n todo-chatbot -- nc -zv todo-chatbot-postgresql 5432
```

### Resource Constraints

```bash
# Increase Minikube resources
minikube stop
minikube delete
minikube start --cpus=4 --memory=8192
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for chatbot |
| `BETTER_AUTH_SECRET` | No | Auth secret (default provided) |
| `DATABASE_URL` | No | Custom database URL |

## Security Considerations

- Secrets are base64 encoded in Kubernetes Secrets
- Use sealed-secrets or external secret management for production
- Backend runs as non-root user (UID 1000)
- Frontend runs as non-root user
- Network policies can be added for additional isolation

## Next Steps

After successful local deployment:

1. Test all chatbot functionality
2. Monitor resource usage with `kubectl top pods`
3. Review logs for any errors
4. Consider adding:
   - Horizontal Pod Autoscaling
   - Network Policies
   - Resource Quotas
   - Pod Disruption Budgets
