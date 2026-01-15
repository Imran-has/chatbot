# Implementation Plan: Todo AI Chatbot

**Branch**: `001-todo-ai-chatbot` | **Date**: 2026-01-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-todo-ai-chatbot/spec.md`

---

## Summary

Build an AI-powered Todo Chatbot that enables users to manage tasks through natural language conversation. The system uses OpenAI Agents SDK for AI reasoning, MCP tools for database operations, FastAPI backend, and OpenAI ChatKit frontend. The architecture is strictly stateless—all state persists in Neon PostgreSQL, allowing seamless server restarts and horizontal scaling.

---

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, OpenAI Agents SDK, MCP SDK, SQLModel, Better Auth
**Storage**: Neon Serverless PostgreSQL
**Testing**: pytest with pytest-asyncio
**Target Platform**: Linux server (containerized), ChatKit web frontend
**Project Type**: Web application (backend + frontend)
**Performance Goals**: <3 second end-to-end latency, 100 concurrent users
**Constraints**: 100% stateless backend, zero in-memory state, MCP-only database access
**Scale/Scope**: Single user deployment initially, scalable to multi-tenant

---

## Constitution Check

*GATE: Must pass before implementation begins.*

| Principle | Requirement | Implementation Approach |
|-----------|-------------|------------------------|
| I. MCP-First Execution | All DB operations via MCP tools | MCP server with 5 stateless tools; AI has NO direct DB access |
| II. Intent Recognition | Classify intent before action | Agent system prompt with intent mapping; clarification on ambiguity |
| III. Stateless Operation | No in-memory state | All state in PostgreSQL; history loaded per request |
| IV. Graceful Error Handling | User-friendly errors | Error translation layer; no stack traces to users |
| V. Confirmation-Driven Feedback | Confirm every action | Response templates with ✅ confirmations |
| VI. Minimal Data Modification | Only modify requested fields | Update tools accept optional fields; unchanged = untouched |

**Result**: ✅ All principles addressable in design

---

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-ai-chatbot/
├── spec.md              # Feature specification (completed)
├── plan.md              # This implementation plan
└── tasks.md             # Task breakdown (next: /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py           # Task SQLModel
│   │   ├── conversation.py   # Conversation SQLModel
│   │   └── message.py        # Message SQLModel
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py         # MCP server setup
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── add_task.py
│   │       ├── list_tasks.py
│   │       ├── complete_task.py
│   │       ├── delete_task.py
│   │       └── update_task.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── chat_agent.py     # OpenAI Agent configuration
│   │   └── prompts.py        # System prompts and intent mapping
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat.py           # POST /api/{user_id}/chat
│   │   └── health.py         # Health check endpoint
│   ├── db/
│   │   ├── __init__.py
│   │   ├── connection.py     # Neon PostgreSQL connection
│   │   └── migrations/       # Alembic migrations
│   ├── auth/
│   │   ├── __init__.py
│   │   └── better_auth.py    # Better Auth integration
│   └── main.py               # FastAPI app entry point
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── requirements.txt
├── pyproject.toml
└── Dockerfile

frontend/
├── src/
│   ├── components/
│   │   └── ChatInterface.tsx  # ChatKit wrapper
│   ├── lib/
│   │   └── api.ts            # API client
│   └── app/
│       └── page.tsx          # Main chat page
├── .env.local                # NEXT_PUBLIC_OPENAI_DOMAIN_KEY
└── package.json
```

**Structure Decision**: Web application structure (Option 2) selected because the system has distinct backend (FastAPI + MCP) and frontend (ChatKit) components requiring separate deployment and development workflows.

---

## Phase 1: Database & Persistence

### Why This Phase First

The database is the foundation of the stateless architecture. Without persistent storage, the system cannot:
- Resume conversations after server restart
- Store tasks between requests
- Maintain user isolation

All subsequent phases depend on database availability.

### Deliverables

1. **SQLModel Definitions**
   - `Task` model with id, user_id, title, description, completed, created_at, updated_at
   - `Conversation` model with id, user_id, created_at, updated_at
   - `Message` model with id, conversation_id, user_id, role (user/assistant), content, created_at

2. **Database Connection**
   - Neon PostgreSQL connection using SQLModel async engine
   - Connection pooling for concurrent requests
   - Environment variable: `DATABASE_URL`

3. **Migration Setup**
   - Alembic for schema migrations
   - Initial migration creating all three tables
   - Indexes on user_id, conversation_id, created_at

### Validation Criteria

- [ ] Models can be created and queried
- [ ] Foreign key constraint: Message.conversation_id → Conversation.id
- [ ] Timestamps auto-populate on insert
- [ ] Indexes exist for performance-critical queries

---

## Phase 2: MCP Server & Tools

### Why MCP-First

The AI agent MUST NOT access the database directly (Constitution Principle I). MCP tools provide:
- Controlled, auditable interface
- Consistent parameter validation
- User isolation enforcement (every tool requires user_id)
- Stateless operation (no memory between calls)

### MCP Server Setup

- Use official MCP Python SDK
- Register 5 tools with strict schemas
- Each tool: validate input → execute query → return result
- NO state stored in MCP server

### Tool Specifications

#### 1. add_task

| Aspect | Details |
|--------|---------|
| **Input** | user_id (str, required), title (str, required), description (str, optional) |
| **Action** | INSERT into Task table with user_id, title, description, completed=False |
| **Output** | { task_id, status: "created", title } |
| **Errors** | INVALID_TITLE if empty or >500 chars |

#### 2. list_tasks

| Aspect | Details |
|--------|---------|
| **Input** | user_id (str, required), status (str, optional: "all"/"pending"/"completed") |
| **Action** | SELECT from Task WHERE user_id = :user_id, filtered by completed status |
| **Output** | { tasks: [...], count: N } |
| **Errors** | None (empty list is valid) |

#### 3. complete_task

| Aspect | Details |
|--------|---------|
| **Input** | user_id (str, required), task_id (int, required) |
| **Action** | UPDATE Task SET completed=True WHERE id = :task_id AND user_id = :user_id |
| **Output** | { task_id, status: "completed", title } |
| **Errors** | TASK_NOT_FOUND if no match, ALREADY_COMPLETED if already done |

#### 4. delete_task

| Aspect | Details |
|--------|---------|
| **Input** | user_id (str, required), task_id (int, required) |
| **Action** | DELETE FROM Task WHERE id = :task_id AND user_id = :user_id |
| **Output** | { task_id, status: "deleted", title } |
| **Errors** | TASK_NOT_FOUND if no match |

#### 5. update_task

| Aspect | Details |
|--------|---------|
| **Input** | user_id (str, required), task_id (int, required), title (str, optional), description (str, optional) |
| **Action** | UPDATE Task SET title/description WHERE id = :task_id AND user_id = :user_id |
| **Output** | { task_id, status: "updated", title } |
| **Errors** | TASK_NOT_FOUND if no match, NO_CHANGES if no fields provided |

### Statelessness Enforcement

- MCP server holds NO class-level state
- Each tool invocation creates fresh database session
- Session closed after each tool execution
- No caching of user data or task lists

### Validation Criteria

- [ ] Each tool works in isolation
- [ ] User isolation: user A cannot access user B's tasks
- [ ] Error codes returned correctly
- [ ] No state persists between tool calls (restart MCP server, retry same operation)

---

## Phase 3: AI Agent Layer

### Agent Responsibility

The OpenAI Agent acts as a **decision-maker only**:
- Receives conversation history
- Detects user intent from natural language
- Selects appropriate MCP tool(s)
- Formats confirmation response

The agent does NOT:
- Store any state
- Access database directly
- Remember previous conversations (history provided per request)

### System Prompt Design

The agent's system prompt MUST include:
1. Identity as a todo management assistant
2. Available tools and when to use them
3. Intent mapping rules (see spec)
4. Confirmation message templates
5. Error handling instructions
6. Instruction to ask for clarification on ambiguous requests

### Intent Classification

| User Says | Detected Intent | Tool Invoked |
|-----------|-----------------|--------------|
| "Add task buy milk" | CREATE | add_task |
| "Show my tasks" | LIST | list_tasks |
| "I finished the report" | COMPLETE | complete_task |
| "Delete old tasks" | DELETE | delete_task |
| "Change title to..." | UPDATE | update_task |
| "What's pending?" | LIST (filtered) | list_tasks(status="pending") |

### Tool Chaining

When single tool insufficient:
1. **Ambiguous target**: "Complete the milk task"
   - Call list_tasks to find matching task(s)
   - If single match: call complete_task
   - If multiple matches: ask user to clarify
   - If no match: inform user task not found

2. **Bulk operations**: "Delete all completed tasks"
   - Call list_tasks(status="completed")
   - For each task: call delete_task
   - Confirm total deleted

### Response Generation

After tool execution:
- Success: Use confirmation template (e.g., "✅ Task 'buy milk' has been successfully added.")
- Failure: Translate error code to user-friendly message
- Never expose: stack traces, database errors, internal IDs (use task titles)

### Validation Criteria

- [ ] Agent correctly maps 10 sample phrases to tools
- [ ] Tool chaining works for ambiguous requests
- [ ] Confirmation messages match spec templates
- [ ] Errors translated to friendly messages

---

## Phase 4: Stateless Chat API

### Endpoint Design

**Endpoint**: `POST /api/{user_id}/chat`

**Request Flow** (stateless):

```
1. Request arrives with message and optional conversation_id
        ↓
2. Authenticate user via Better Auth (verify user_id matches token)
        ↓
3. If conversation_id missing: CREATE new Conversation in DB
        ↓
4. FETCH all Messages for conversation_id from DB
        ↓
5. STORE user message in DB (role="user")
        ↓
6. Build conversation history array for AI Agent
        ↓
7. INVOKE AI Agent with history
        ↓
8. Agent selects MCP tool(s) and executes
        ↓
9. STORE assistant response in DB (role="assistant")
        ↓
10. RETURN response with conversation_id and tool_calls
```

### Why Each Step Matters

| Step | Why Required |
|------|--------------|
| 2 | Security: ensure user owns their conversation |
| 3 | First message in session needs conversation container |
| 4 | Stateless: server has no memory, must load from DB |
| 5 | Persist before AI call (crash recovery) |
| 7 | AI reasoning with full context |
| 9 | Persist after AI call (conversation continuity) |
| 10 | Client needs conversation_id for future requests |

### Conversation Resumption After Restart

- Server crashes or restarts
- Client sends next message with same conversation_id
- Server loads entire history from database
- AI receives full context as if no restart occurred

**Zero data loss guaranteed** because every message stored before and after AI processing.

### Error Handling

| Error Condition | HTTP Status | Response |
|-----------------|-------------|----------|
| Missing message | 400 | {"error": "message is required"} |
| Invalid auth | 401 | {"error": "authentication required"} |
| Wrong user_id | 403 | {"error": "forbidden"} |
| DB error | 500 | {"error": "something went wrong"} |
| AI error | 500 | {"error": "something went wrong"} |

Never expose internal details. Log full error server-side.

### Validation Criteria

- [ ] New conversation created when conversation_id absent
- [ ] Existing conversation loaded when conversation_id present
- [ ] Messages persisted in correct order
- [ ] Server restart does not break ongoing conversation
- [ ] Response includes all required fields

---

## Phase 5: Frontend (ChatKit)

### ChatKit Responsibilities

OpenAI ChatKit provides:
- Pre-built chat UI components
- Message rendering
- Input handling
- WebSocket/HTTP flexibility

ChatKit does NOT:
- Manage authentication (Better Auth handles this)
- Store conversation state long-term (backend DB does)

### Integration Requirements

1. **Environment Configuration**
   ```
   NEXT_PUBLIC_OPENAI_DOMAIN_KEY=<your-domain-key>
   ```
   Required for hosted ChatKit deployment.

2. **API Connection**
   - Endpoint: `POST /api/{user_id}/chat`
   - Headers: `Authorization: Bearer <token>`, `Content-Type: application/json`
   - Body: `{ conversation_id?, message }`

3. **State Management**
   - Store `conversation_id` in React state after first response
   - Pass `conversation_id` with every subsequent message
   - Provide "New Conversation" button that clears `conversation_id`

4. **Domain Allowlist**
   - Configure ChatKit allowed domains for CORS
   - Backend must accept requests from frontend domain

### Message Display

- User messages: right-aligned, distinct color
- Assistant messages: left-aligned, include ✅ confirmations
- Tool calls: optionally show in debug mode (collapsed by default)

### Validation Criteria

- [ ] Chat UI renders and accepts input
- [ ] Messages sent to correct endpoint
- [ ] conversation_id persisted across messages
- [ ] New conversation clears previous context

---

## Phase 6: Error Handling & UX

### Error Translation Layer

Backend translates all errors to user-friendly messages:

| Internal Error | User-Facing Message |
|----------------|---------------------|
| TASK_NOT_FOUND | "I couldn't find that task. Would you like me to show your current tasks?" |
| ALREADY_COMPLETED | "That task is already marked as complete." |
| INVALID_TITLE | "The task title seems too long. Could you shorten it a bit?" |
| DATABASE_ERROR | "I'm having trouble right now. Please try again in a moment." |
| OPENAI_ERROR | "I'm having trouble right now. Please try again in a moment." |
| AUTH_ERROR | "Please sign in to continue." |

### Confirmation Patterns

Every successful operation returns explicit confirmation:

| Action | Confirmation |
|--------|--------------|
| Create | "✅ Task '[title]' has been successfully added." |
| Complete | "✅ Task '[title]' has been marked as complete." |
| Delete | "✅ Task '[title]' has been removed." |
| Update | "✅ Task '[title]' has been updated." |
| List (empty) | "You don't have any [status] tasks right now." |
| List (results) | "Here are your tasks: [formatted list]" |

### UX Principles

1. **Never leave user confused**: Every response either confirms success or explains failure
2. **Suggest next action**: On error, offer helpful alternative (e.g., "show your tasks")
3. **No technical jargon**: Avoid IDs, error codes, SQL errors in user-facing text
4. **Friendly tone**: Polite, concise, action-oriented

### Validation Criteria

- [ ] All error codes have user-friendly mappings
- [ ] Confirmations match spec templates
- [ ] No stack traces or internal errors exposed
- [ ] Graceful degradation on service outages

---

## Phase 7: Testing & Validation

### Test Categories

#### 1. Stateless Validation Tests

Verify the system holds no in-memory state:

| Test | Procedure | Expected Result |
|------|-----------|-----------------|
| Restart resilience | Create task → restart server → list tasks | Task persists |
| Conversation continuity | Send 3 messages → restart → send 4th | History includes all 4 |
| No cross-request memory | Request A creates task → Request B (new session) lists | Task visible |

#### 2. MCP Tool Correctness Tests

| Tool | Test Case | Expected |
|------|-----------|----------|
| add_task | Valid title | Task created, ID returned |
| add_task | Empty title | INVALID_TITLE error |
| list_tasks | No tasks | Empty array, count=0 |
| list_tasks | With filter | Only matching status returned |
| complete_task | Valid task | completed=True |
| complete_task | Wrong user | TASK_NOT_FOUND |
| delete_task | Valid task | Task removed from DB |
| update_task | Title only | Title changes, description unchanged |

#### 3. Agent Intent Tests

| Input | Expected Tool |
|-------|---------------|
| "Add buy milk" | add_task |
| "Show tasks" | list_tasks |
| "Done with laundry" | complete_task |
| "Remove old task" | delete_task |
| "Change title to X" | update_task |
| "What's pending?" | list_tasks(status="pending") |

#### 4. End-to-End Tests

| Scenario | Steps | Validation |
|----------|-------|------------|
| Full lifecycle | Create → List → Complete → Delete | Each step succeeds |
| Error recovery | Complete non-existent task | User-friendly error returned |
| Auth enforcement | Request with wrong user_id | 403 Forbidden |

### Validation Criteria

- [ ] All stateless tests pass
- [ ] All MCP tool tests pass
- [ ] Intent classification >95% accuracy on test set
- [ ] E2E scenarios complete without errors

---

## Phase 8: Documentation & Deployment

### Repository Structure

```text
/
├── backend/                  # FastAPI + MCP server
│   ├── src/
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md            # Backend-specific docs
├── frontend/                 # ChatKit frontend
│   ├── src/
│   ├── package.json
│   └── README.md            # Frontend-specific docs
├── specs/                    # Design documents
│   └── 001-todo-ai-chatbot/
│       ├── spec.md
│       ├── plan.md
│       └── tasks.md
├── .specify/                 # SpecKit Plus configuration
├── README.md                 # Project overview
├── docker-compose.yml        # Full stack orchestration
└── .env.example             # Required environment variables
```

### README Requirements

The root README MUST include:

1. **Project Overview**: What the system does (1 paragraph)
2. **Architecture Diagram**: ASCII or image showing data flow
3. **Technology Stack**: Table of components and versions
4. **Quick Start**: Steps to run locally
5. **Environment Variables**: All required config with descriptions
6. **API Documentation**: Endpoint, request/response examples
7. **Stateless Design**: Explanation of why and how
8. **MCP Tools**: List of available tools with descriptions

### Deployment Artifacts

- `Dockerfile` for backend (multi-stage build)
- `docker-compose.yml` for local development (backend + Neon + frontend)
- `.env.example` with all required variables documented
- Database migration scripts

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | Neon PostgreSQL connection | postgres://... |
| OPENAI_API_KEY | OpenAI API key for Agent | sk-... |
| BETTER_AUTH_SECRET | Authentication secret | random-string |
| NEXT_PUBLIC_OPENAI_DOMAIN_KEY | ChatKit domain key | key-... |

### Validation Criteria

- [ ] README complete with all required sections
- [ ] Docker build succeeds
- [ ] docker-compose up starts full stack
- [ ] .env.example documents all required variables

---

## Complexity Tracking

No Constitution violations requiring justification. All principles are met with standard implementation patterns.

---

## Execution Order Summary

| Phase | Depends On | Deliverables |
|-------|------------|--------------|
| 1. Database | None | Models, migrations, connection |
| 2. MCP Server | Phase 1 | 5 stateless tools |
| 3. AI Agent | Phase 2 | Intent mapping, tool chaining |
| 4. Chat API | Phase 1, 2, 3 | Stateless endpoint |
| 5. Frontend | Phase 4 | ChatKit integration |
| 6. Error Handling | Phase 4 | Translation layer, UX |
| 7. Testing | All phases | Test suites |
| 8. Documentation | All phases | README, deployment |

---

## Next Steps

Run `/sp.tasks` to generate detailed, actionable task breakdown from this plan.
