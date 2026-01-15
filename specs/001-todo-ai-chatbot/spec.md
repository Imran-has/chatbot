# Feature Specification: Todo AI Chatbot

**Feature Branch**: `001-todo-ai-chatbot`
**Created**: 2026-01-06
**Status**: Draft
**Input**: Full-stack Todo AI Chatbot with stateless architecture and MCP-based tool design

---

## System Overview

The Todo AI Chatbot is an AI-powered task management system that allows users to manage tasks through natural language conversation. The system enforces strict separation between the AI agent and data persistence through MCP (Model Context Protocol) tools.

### Technology Stack

| Component | Technology |
|-----------|------------|
| AI Framework | OpenAI Agents SDK |
| Tool Protocol | MCP (Model Context Protocol) |
| Backend | FastAPI (Python) |
| Database | Neon Serverless PostgreSQL |
| ORM | SQLModel |
| Frontend | OpenAI ChatKit |
| Authentication | Better Auth |

### Architecture Principles

1. **Stateless Backend**: Server holds NO in-memory state; all state persisted in database
2. **MCP-First**: AI NEVER directly accesses database; ALL operations via MCP tools
3. **Request Independence**: Each chat request handled independently with fresh context
4. **Conversation Continuity**: History fetched from database per request

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Tasks via Chat (Priority: P1)

A user wants to add a new task to their todo list by typing a natural language message like "Add a task to buy groceries" or "Remember to call mom tomorrow".

**Why this priority**: Task creation is the fundamental capability. Without it, the system has no value. This must work flawlessly before any other feature.

**Independent Test**: Send a chat message containing "add task [title]" and verify the task appears in the database with correct user_id, title, and pending status.

**Acceptance Scenarios**:

1. **Given** a user is in a chat session, **When** they type "Add a task to buy groceries", **Then** the system creates a task with title "buy groceries" and responds "✅ Task 'buy groceries' has been successfully added."

2. **Given** a user types "Remember to submit the report by Friday", **When** the AI processes the message, **Then** a task is created with title "submit the report by Friday" and confirmation is returned.

3. **Given** a user provides a task with description "Create task: Review PR with details: Check for security issues", **When** processed, **Then** task is created with title "Review PR" and description "Check for security issues".

---

### User Story 2 - List Tasks (Priority: P1)

A user wants to view their current tasks, optionally filtered by status (pending, completed, or all).

**Why this priority**: Users need to see their tasks to take further action. This is essential for task management and enables completion/deletion workflows.

**Independent Test**: After creating 3 tasks (2 pending, 1 completed), request "show my pending tasks" and verify only the 2 pending tasks are returned.

**Acceptance Scenarios**:

1. **Given** a user has 5 tasks (3 pending, 2 completed), **When** they ask "Show my tasks", **Then** all 5 tasks are listed with their status indicators.

2. **Given** a user has pending and completed tasks, **When** they ask "What's pending?", **Then** only pending tasks are returned.

3. **Given** a user has no tasks, **When** they ask "List my tasks", **Then** the response indicates no tasks found and suggests creating one.

---

### User Story 3 - Complete Tasks (Priority: P2)

A user wants to mark a task as completed by referring to it by name or ID.

**Why this priority**: After creating and viewing tasks, completion is the core workflow. Essential for task lifecycle but requires list functionality first.

**Independent Test**: Create a task, then send "mark [task] as done" and verify the task's completed field is true.

**Acceptance Scenarios**:

1. **Given** a user has a task titled "buy groceries", **When** they say "I finished buying groceries", **Then** the task is marked complete with confirmation "✅ Task 'buy groceries' has been marked as complete."

2. **Given** a user has multiple tasks with similar names, **When** they say "complete the report task", **Then** the system lists matching tasks and asks for clarification.

3. **Given** a user references a non-existent task, **When** they say "complete my vacation task", **Then** the system responds with "I couldn't find that task. Would you like me to show your current tasks?"

---

### User Story 4 - Delete Tasks (Priority: P2)

A user wants to remove a task from their list permanently.

**Why this priority**: Deletion is necessary for list hygiene but less frequently used than completion. Requires confirmation to prevent accidental data loss.

**Independent Test**: Create a task, delete it via chat, and verify it no longer appears in list_tasks results.

**Acceptance Scenarios**:

1. **Given** a user has a task titled "old reminder", **When** they say "delete the old reminder task", **Then** the task is deleted with confirmation "✅ Task 'old reminder' has been removed."

2. **Given** ambiguous task reference, **When** user says "remove my task", **Then** system lists tasks and asks which one to delete.

---

### User Story 5 - Update Tasks (Priority: P3)

A user wants to modify the title or description of an existing task.

**Why this priority**: Updates are less common than create/complete/delete. Most users create new tasks rather than editing existing ones.

**Independent Test**: Create a task, update its title via "rename [old] to [new]", verify the change persists.

**Acceptance Scenarios**:

1. **Given** a task titled "call mom", **When** user says "change 'call mom' to 'call mom at 5pm'", **Then** the title is updated with confirmation.

2. **Given** a task without description, **When** user says "add description to 'meeting' task: discuss Q4 goals", **Then** description field is updated while title remains unchanged.

---

### User Story 6 - Conversation Continuity (Priority: P2)

A user's conversation history persists across server restarts, allowing context-aware responses.

**Why this priority**: Critical for production deployment. Without persistence, server restarts break user experience.

**Independent Test**: Start conversation, restart server, continue conversation and verify history is intact.

**Acceptance Scenarios**:

1. **Given** a conversation with 5 messages, **When** server restarts, **Then** the next message receives full context of previous 5 messages.

2. **Given** user references "the task I just created", **When** AI processes the request, **Then** it correctly identifies the most recent task from conversation history.

---

### User Story 7 - New Conversation (Priority: P3)

A user can start a fresh conversation without previous context.

**Why this priority**: Allows users to reset context when needed, but not essential for core functionality.

**Independent Test**: Send message without conversation_id and verify new conversation is created.

**Acceptance Scenarios**:

1. **Given** a user with existing conversations, **When** they send a message without conversation_id, **Then** a new conversation is created and the response includes the new conversation_id.

---

### Edge Cases

- What happens when user sends empty message? → Return friendly prompt to ask what they'd like to do
- What happens when task title exceeds maximum length? → Truncate with warning or reject with character limit guidance
- How does system handle concurrent task operations on same task? → Last-write-wins with timestamp checking
- What happens when database connection fails? → Return graceful error: "I'm having trouble right now. Please try again in a moment."
- How does system handle special characters in task titles? → Sanitize input, allow safe special characters
- What happens when user_id is missing or invalid? → Authentication layer rejects request before reaching AI

---

## Requirements *(mandatory)*

### Functional Requirements

#### Core Chat API

- **FR-001**: System MUST expose `POST /api/{user_id}/chat` endpoint accepting JSON body with `message` (required) and `conversation_id` (optional)
- **FR-002**: System MUST create new conversation when `conversation_id` is not provided
- **FR-003**: System MUST fetch complete conversation history from database before AI processing
- **FR-004**: System MUST persist user message to database before AI invocation
- **FR-005**: System MUST persist assistant response to database after AI generates response
- **FR-006**: System MUST return JSON response containing `conversation_id`, `response`, and `tool_calls` array

#### MCP Tool Requirements

- **FR-007**: AI MUST invoke `add_task` tool with `user_id`, `title`, and optional `description` to create tasks
- **FR-008**: AI MUST invoke `list_tasks` tool with `user_id` and optional `status` filter to retrieve tasks
- **FR-009**: AI MUST invoke `complete_task` tool with `user_id` and `task_id` to mark tasks complete
- **FR-010**: AI MUST invoke `delete_task` tool with `user_id` and `task_id` to remove tasks
- **FR-011**: AI MUST invoke `update_task` tool with `user_id`, `task_id`, and fields to modify

#### AI Behavior Requirements

- **FR-012**: AI MUST detect user intent before selecting MCP tool (per Constitution Principle II)
- **FR-013**: AI MUST confirm every successful operation with clear feedback (per Constitution Principle V)
- **FR-014**: AI MUST handle errors gracefully with user-friendly messages (per Constitution Principle IV)
- **FR-015**: AI MUST only modify fields explicitly requested by user (per Constitution Principle VI)
- **FR-016**: AI MUST chain multiple MCP tools when necessary (e.g., list before complete when task_id unknown)

#### Stateless Architecture Requirements

- **FR-017**: Backend server MUST hold NO in-memory state between requests
- **FR-018**: Each request MUST be processed independently using only database state
- **FR-019**: Server restart MUST NOT lose any conversation or task data

#### Authentication Requirements

- **FR-020**: System MUST authenticate users via Better Auth before processing requests
- **FR-021**: System MUST validate `user_id` in path matches authenticated user
- **FR-022**: All MCP tools MUST receive `user_id` to scope operations to authenticated user

### Key Entities

- **Task**: Represents a user's todo item with id, user_id, title, optional description, completed status, and timestamps (created_at, updated_at)

- **Conversation**: Represents a chat session with id, user_id, and timestamps. One user can have multiple conversations.

- **Message**: Represents a single message in a conversation with id, conversation_id, user_id, role (user/assistant), content, and created_at timestamp. Ordered chronologically within conversation.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task via chat in under 3 seconds (end-to-end latency)
- **SC-002**: System correctly classifies user intent with 95%+ accuracy across supported operations
- **SC-003**: 100% of successful operations return explicit confirmation messages
- **SC-004**: System handles 100 concurrent chat requests without degradation
- **SC-005**: Server can restart and resume conversations within 5 seconds
- **SC-006**: 0% of error responses expose internal system details or stack traces
- **SC-007**: All task operations are correctly scoped to user_id (no cross-user data access)

---

## System Architecture

### High-Level Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   ChatKit   │────▶│   FastAPI   │────▶│  OpenAI     │────▶│    MCP      │
│  Frontend   │     │   Backend   │     │  Agent SDK  │     │   Tools     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                   │                   │
                           │                   │                   │
                           ▼                   │                   ▼
                    ┌─────────────┐            │           ┌─────────────┐
                    │   Neon      │◀───────────┘           │    Neon     │
                    │ PostgreSQL  │                        │  PostgreSQL │
                    │(Conversations)                       │   (Tasks)   │
                    └─────────────┘                        └─────────────┘
```

### Stateless Request Flow

1. **Request Arrives**: `POST /api/{user_id}/chat` with message and optional conversation_id
2. **Conversation Resolution**: Create new or fetch existing conversation
3. **History Retrieval**: Load all messages for conversation_id from database
4. **Message Persistence**: Store user message in database
5. **AI Invocation**: Pass conversation history to OpenAI Agent
6. **Tool Execution**: Agent selects and calls MCP tool(s) as needed
7. **Response Persistence**: Store assistant response in database
8. **Response Return**: Send response to client with conversation_id and tool_calls

### Why Stateless?

| Concern | Stateless Solution |
|---------|-------------------|
| Server crashes | No in-memory state lost; resume from database |
| Horizontal scaling | Any server can handle any request |
| Debugging | Request fully reproducible from database state |
| Deployment | Zero-downtime restarts possible |

---

## API Contracts

### Chat Endpoint

**Endpoint**: `POST /api/{user_id}/chat`

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | Authenticated user identifier |

**Request Body**:
```json
{
  "conversation_id": 123,
  "message": "Add a task to buy groceries"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| conversation_id | integer | No | Existing conversation ID. If omitted, new conversation created. |
| message | string | Yes | User's natural language message |

**Response Body**:
```json
{
  "conversation_id": 123,
  "response": "✅ Task 'buy groceries' has been successfully added.",
  "tool_calls": [
    {
      "tool": "add_task",
      "arguments": {
        "user_id": "user_abc",
        "title": "buy groceries"
      },
      "result": {
        "task_id": 456,
        "status": "created",
        "title": "buy groceries"
      }
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| conversation_id | integer | Conversation ID (existing or newly created) |
| response | string | AI-generated response text |
| tool_calls | array | List of MCP tools invoked with arguments and results |

**Error Responses**:
| Status | Condition | Response |
|--------|-----------|----------|
| 400 | Missing message | `{"error": "message is required"}` |
| 401 | Unauthorized | `{"error": "authentication required"}` |
| 403 | user_id mismatch | `{"error": "forbidden"}` |
| 500 | Internal error | `{"error": "something went wrong"}` |

---

## MCP Tool Definitions

### add_task

**Purpose**: Create a new task for the user

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| user_id | string | Yes | Owner of the task |
| title | string | Yes | Task title (1-500 characters) |
| description | string | No | Additional details |

**Returns**:
```json
{
  "task_id": 123,
  "status": "created",
  "title": "buy groceries"
}
```

**Errors**:
| Code | Condition |
|------|-----------|
| INVALID_TITLE | Title empty or exceeds 500 chars |
| USER_NOT_FOUND | Invalid user_id |

---

### list_tasks

**Purpose**: Retrieve user's tasks with optional filtering

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| user_id | string | Yes | Owner of tasks |
| status | string | No | Filter: "all" (default), "pending", "completed" |

**Returns**:
```json
{
  "tasks": [
    {
      "task_id": 123,
      "title": "buy groceries",
      "description": null,
      "completed": false,
      "created_at": "2026-01-06T10:00:00Z"
    }
  ],
  "count": 1
}
```

---

### complete_task

**Purpose**: Mark a task as completed

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| user_id | string | Yes | Owner of the task |
| task_id | integer | Yes | Task to complete |

**Returns**:
```json
{
  "task_id": 123,
  "status": "completed",
  "title": "buy groceries"
}
```

**Errors**:
| Code | Condition |
|------|-----------|
| TASK_NOT_FOUND | Task doesn't exist or wrong user |
| ALREADY_COMPLETED | Task already marked complete |

---

### delete_task

**Purpose**: Permanently remove a task

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| user_id | string | Yes | Owner of the task |
| task_id | integer | Yes | Task to delete |

**Returns**:
```json
{
  "task_id": 123,
  "status": "deleted",
  "title": "buy groceries"
}
```

**Errors**:
| Code | Condition |
|------|-----------|
| TASK_NOT_FOUND | Task doesn't exist or wrong user |

---

### update_task

**Purpose**: Modify task title or description

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| user_id | string | Yes | Owner of the task |
| task_id | integer | Yes | Task to update |
| title | string | No | New title (if changing) |
| description | string | No | New description (if changing) |

**Returns**:
```json
{
  "task_id": 123,
  "status": "updated",
  "title": "buy groceries at costco"
}
```

**Errors**:
| Code | Condition |
|------|-----------|
| TASK_NOT_FOUND | Task doesn't exist or wrong user |
| NO_CHANGES | Neither title nor description provided |

---

## Database Schema

### Task Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique task identifier |
| user_id | VARCHAR(255) | NOT NULL, INDEX | Owner's user ID |
| title | VARCHAR(500) | NOT NULL | Task title |
| description | TEXT | NULLABLE | Optional details |
| completed | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last modification |

### Conversation Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique conversation ID |
| user_id | VARCHAR(255) | NOT NULL, INDEX | Owner's user ID |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last activity |

### Message Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique message ID |
| conversation_id | INTEGER | NOT NULL, FOREIGN KEY | Parent conversation |
| user_id | VARCHAR(255) | NOT NULL | Message author |
| role | ENUM('user','assistant') | NOT NULL | Message sender type |
| content | TEXT | NOT NULL | Message content |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Message timestamp |

**Indexes**:
- `idx_task_user_id` on Task(user_id)
- `idx_conversation_user_id` on Conversation(user_id)
- `idx_message_conversation_id` on Message(conversation_id)
- `idx_message_created_at` on Message(created_at)

---

## AI Agent Behavior Rules

### Intent Detection

The agent MUST classify user intent before selecting an MCP tool:

| Intent Category | Trigger Words | MCP Tool |
|-----------------|---------------|----------|
| Create | add, create, remember, new, I need to | `add_task` |
| List | show, list, what's, view, display | `list_tasks` |
| Complete | done, complete, finished, mark | `complete_task` |
| Delete | delete, remove, cancel, drop | `delete_task` |
| Update | change, update, rename, edit, modify | `update_task` |

### Tool Chaining

When the user's request requires multiple operations:

1. **Ambiguous completion**: "Mark my last task as done"
   - First: `list_tasks` to find most recent task
   - Then: `complete_task` with identified task_id

2. **Bulk operations**: "Delete all completed tasks"
   - First: `list_tasks` with status="completed"
   - Then: `delete_task` for each task (or confirm before bulk delete)

### Error Recovery

Per Constitution Principle IV, errors MUST be handled gracefully:

| Error Type | User-Facing Response |
|------------|---------------------|
| TASK_NOT_FOUND | "I couldn't find that task. Would you like me to show your current tasks?" |
| ALREADY_COMPLETED | "That task is already marked as complete." |
| INVALID_TITLE | "The task title seems too long. Could you shorten it a bit?" |
| DATABASE_ERROR | "I'm having trouble right now. Please try again in a moment." |

### Confirmation Messages

Per Constitution Principle V, every action MUST be confirmed:

| Action | Confirmation Template |
|--------|----------------------|
| Create | "✅ Task '[title]' has been successfully added." |
| Complete | "✅ Task '[title]' has been marked as complete." |
| Delete | "✅ Task '[title]' has been removed." |
| Update | "✅ Task '[title]' has been updated." |
| List (empty) | "You don't have any [pending/completed] tasks right now." |
| List (results) | "Here are your [pending/completed/all] tasks: [list]" |

---

## Frontend Integration

### ChatKit Configuration

The frontend uses OpenAI ChatKit with hosted deployment:

**Environment Variables**:
```
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=<your-domain-key>
```

**API Connection**:
- Endpoint: `POST /api/{user_id}/chat`
- Content-Type: `application/json`
- Authorization: Bearer token from Better Auth

**State Management**:
- Store `conversation_id` in component state
- Pass `conversation_id` with each request after first response
- Clear `conversation_id` to start new conversation

---

## Security Considerations

1. **User Isolation**: All MCP tools require `user_id` parameter; database queries MUST filter by user_id
2. **Input Sanitization**: Task titles and descriptions MUST be sanitized before storage
3. **Authentication**: All `/api/{user_id}/*` endpoints require Better Auth validation
4. **Authorization**: Path `user_id` MUST match authenticated user's ID
5. **No Direct DB Access**: AI agent CANNOT execute raw SQL; only MCP tools

---

## Constitution Compliance

This specification adheres to all six Constitutional Principles:

| Principle | Compliance |
|-----------|------------|
| I. MCP-First Execution | All task operations via MCP tools only (FR-007 through FR-011) |
| II. Intent Recognition | Intent classification before tool selection (FR-012) |
| III. Stateless Operation | No in-memory state; database-driven (FR-017, FR-018, FR-019) |
| IV. Graceful Error Handling | User-friendly error messages (FR-014) |
| V. Confirmation-Driven Feedback | Explicit confirmations for all actions (FR-013) |
| VI. Minimal Data Modification | Only modify explicitly requested fields (FR-015) |
