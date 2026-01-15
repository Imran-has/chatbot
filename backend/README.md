# Todo AI Chatbot - Backend

FastAPI backend for the Todo AI Chatbot, providing a natural language interface for task management via MCP tools.

## Prerequisites

- Python 3.11+
- PostgreSQL (Neon or local)
- OpenAI API key

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `OPENAI_MODEL` | Model to use (default: gpt-4-turbo-preview) | No |
| `BETTER_AUTH_SECRET` | Secret for JWT tokens | Yes |
| `CORS_ORIGINS` | Comma-separated allowed origins | No |

## API Endpoints

### Health Check
```
GET /health
```

### Chat
```
POST /api/{user_id}/chat
Content-Type: application/json

{
  "message": "Add a task to buy groceries",
  "conversation_id": 1  // optional
}
```

Response:
```json
{
  "conversation_id": 1,
  "response": "I've added 'buy groceries' to your task list.",
  "tool_calls": [
    {
      "tool": "add_task",
      "arguments": {"user_id": "...", "title": "buy groceries"},
      "result": {"task_id": 1, "status": "pending", "title": "buy groceries"}
    }
  ]
}
```

## Architecture

- **Stateless**: No in-memory state - all data in PostgreSQL
- **MCP-First**: AI uses MCP tools exclusively for database operations
- **User Isolation**: All operations scoped by user_id

## Project Structure

```
backend/
├── src/
│   ├── api/           # FastAPI routes
│   ├── agent/         # OpenAI chat agent
│   ├── auth/          # Better Auth integration
│   ├── db/            # Database connection & migrations
│   ├── mcp/           # MCP server & tools
│   ├── models/        # SQLModel definitions
│   ├── utils/         # Error handling utilities
│   ├── errors.py      # Error codes enum
│   └── main.py        # FastAPI app entry point
└── requirements.txt
```
