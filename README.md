# Todo AI Chatbot

An AI-powered task management system that lets you manage your todo list through natural language conversation.

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│     Backend     │────▶│   PostgreSQL    │
│  (Next.js)      │     │   (FastAPI)     │     │    (Neon)       │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                        ┌────────▼────────┐
                        │   OpenAI API    │
                        │  (GPT-4 Agent)  │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │   MCP Tools     │
                        │ (Task CRUD)     │
                        └─────────────────┘
```

### Key Design Principles

1. **Stateless Backend**: No in-memory state - all data persisted in PostgreSQL
2. **MCP-First**: AI agent uses MCP tools exclusively for database operations
3. **User Isolation**: All operations scoped by user_id
4. **Conversation Continuity**: Chat history survives server restarts

## Quick Start

### Using Docker Compose

```bash
# Clone and navigate to project
cd todo-ai-chatbot

# Create environment files
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# Edit .env files with your credentials:
# - DATABASE_URL (PostgreSQL connection string)
# - OPENAI_API_KEY (OpenAI API key)
# - BETTER_AUTH_SECRET (random string for JWT)

# Start all services
docker-compose up -d

# Access:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Manual Setup

See individual README files:
- [Backend README](./backend/README.md)
- [Frontend README](./frontend/README.md)

## API Reference

### POST /api/{user_id}/chat

Send a chat message and receive an AI response.

**Request:**
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": 1
}
```

**Response:**
```json
{
  "conversation_id": 1,
  "response": "I've added 'buy groceries' to your task list.",
  "tool_calls": [
    {
      "tool": "add_task",
      "arguments": {"user_id": "user-123", "title": "buy groceries"},
      "result": {"task_id": 1, "status": "pending", "title": "buy groceries"}
    }
  ]
}
```

### GET /health

Health check endpoint for monitoring.

## MCP Tools

The AI agent has access to these tools for task management:

| Tool | Description | Parameters |
|------|-------------|------------|
| `add_task` | Create a new task | `title`, `description?` |
| `list_tasks` | List user's tasks | `status?` (all/pending/completed) |
| `complete_task` | Mark task as done | `task_id` |
| `delete_task` | Remove a task | `task_id` |
| `update_task` | Modify task details | `task_id`, `title?`, `description?` |

## Environment Variables

### Backend

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `OPENAI_MODEL` | OpenAI model to use | No | gpt-4-turbo-preview |
| `BETTER_AUTH_SECRET` | JWT signing secret | Yes | - |
| `CORS_ORIGINS` | Allowed CORS origins | No | http://localhost:3000 |

### Frontend

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes | http://localhost:8000 |

## Project Structure

```
todo-ai-chatbot/
├── backend/
│   ├── src/
│   │   ├── api/           # FastAPI routes
│   │   ├── agent/         # OpenAI chat agent
│   │   ├── auth/          # Authentication
│   │   ├── db/            # Database & migrations
│   │   ├── mcp/           # MCP server & tools
│   │   ├── models/        # SQLModel definitions
│   │   ├── utils/         # Utilities
│   │   └── main.py        # App entry point
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js pages
│   │   ├── components/    # React components
│   │   └── lib/           # API client
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Database Migrations

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```
