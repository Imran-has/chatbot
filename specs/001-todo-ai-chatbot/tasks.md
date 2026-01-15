# Tasks: Todo AI Chatbot

**Input**: Design documents from `/specs/001-todo-ai-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Tests are NOT explicitly requested in the specification. Test tasks omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Backend: Python 3.11+, FastAPI, SQLModel, MCP SDK
- Frontend: Next.js with ChatKit

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for both backend and frontend

- [x] T001 Create backend directory structure per plan.md in backend/
- [x] T002 Create frontend directory structure per plan.md in frontend/
- [x] T003 [P] Initialize Python project with pyproject.toml in backend/pyproject.toml
- [x] T004 [P] Initialize Next.js project with package.json in frontend/package.json
- [x] T005 [P] Create requirements.txt with FastAPI, SQLModel, MCP SDK, OpenAI SDK, Better Auth in backend/requirements.txt
- [x] T006 [P] Configure .env.example with DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET in backend/.env.example
- [x] T007 [P] Configure .env.example with NEXT_PUBLIC_OPENAI_DOMAIN_KEY in frontend/.env.example
- [x] T008 Create docker-compose.yml for local development at repository root

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

### Database Layer

- [x] T009 Create database connection module with async SQLModel engine in backend/src/db/connection.py
- [x] T010 [P] Create Task SQLModel with id, user_id, title, description, completed, timestamps in backend/src/models/task.py
- [x] T011 [P] Create Conversation SQLModel with id, user_id, timestamps in backend/src/models/conversation.py
- [x] T012 [P] Create Message SQLModel with id, conversation_id, user_id, role, content, created_at in backend/src/models/message.py
- [x] T013 Create models __init__.py exporting all models in backend/src/models/__init__.py
- [x] T014 Setup Alembic migrations framework in backend/src/db/migrations/
- [x] T015 Create initial migration for Task, Conversation, Message tables with indexes in backend/src/db/migrations/versions/

### MCP Server Foundation

- [x] T016 Create MCP server base setup using MCP Python SDK in backend/src/mcp/server.py
- [x] T017 Create MCP tools __init__.py with tool registration in backend/src/mcp/tools/__init__.py

### Authentication Layer

- [x] T018 Implement Better Auth integration for user authentication in backend/src/auth/better_auth.py
- [x] T019 Create auth middleware for FastAPI request validation in backend/src/auth/__init__.py

### API Foundation

- [x] T020 Create FastAPI application entry point with CORS in backend/src/main.py
- [x] T021 [P] Create health check endpoint in backend/src/api/health.py
- [x] T022 Create API router initialization in backend/src/api/__init__.py

### Error Handling Infrastructure

- [x] T023 Create error codes enum (TASK_NOT_FOUND, INVALID_TITLE, etc.) in backend/src/errors.py
- [x] T024 Create error translation layer for user-friendly messages in backend/src/utils/error_handler.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Create Tasks via Chat (Priority: P1)

**Goal**: Users can add tasks to their todo list via natural language chat messages

**Independent Test**: Send "add task buy groceries" and verify task created in database with confirmation message

### MCP Tool for US1

- [x] T025 [US1] Implement add_task MCP tool with user_id, title, description params in backend/src/mcp/tools/add_task.py
- [x] T026 [US1] Add input validation for title (1-500 chars, non-empty) in backend/src/mcp/tools/add_task.py
- [x] T027 [US1] Register add_task tool with MCP server in backend/src/mcp/server.py

### AI Agent for US1

- [x] T028 [US1] Create system prompt with CREATE intent mapping in backend/src/agent/prompts.py
- [x] T029 [US1] Implement chat agent with OpenAI Agents SDK in backend/src/agent/chat_agent.py
- [x] T030 [US1] Configure agent to use add_task tool for create intents in backend/src/agent/chat_agent.py
- [x] T031 [US1] Add confirmation message template for task creation in backend/src/agent/prompts.py

### Chat API for US1

- [x] T032 [US1] Create POST /api/{user_id}/chat endpoint skeleton in backend/src/api/chat.py
- [x] T033 [US1] Implement conversation creation when conversation_id absent in backend/src/api/chat.py
- [x] T034 [US1] Implement conversation history fetch from database in backend/src/api/chat.py
- [x] T035 [US1] Implement user message persistence before AI call in backend/src/api/chat.py
- [x] T036 [US1] Implement AI agent invocation with history in backend/src/api/chat.py
- [x] T037 [US1] Implement assistant response persistence after AI call in backend/src/api/chat.py
- [x] T038 [US1] Return JSON response with conversation_id, response, tool_calls in backend/src/api/chat.py

**Checkpoint**: User Story 1 complete - can create tasks via chat

---

## Phase 4: User Story 2 - List Tasks (Priority: P1)

**Goal**: Users can view their tasks with optional status filtering (pending/completed/all)

**Independent Test**: Create 3 tasks, ask "show my pending tasks", verify correct filtering

### MCP Tool for US2

- [x] T039 [US2] Implement list_tasks MCP tool with user_id, status params in backend/src/mcp/tools/list_tasks.py
- [x] T040 [US2] Add status filter logic (all/pending/completed) in backend/src/mcp/tools/list_tasks.py
- [x] T041 [US2] Return tasks array with count in backend/src/mcp/tools/list_tasks.py
- [x] T042 [US2] Register list_tasks tool with MCP server in backend/src/mcp/server.py

### AI Agent Update for US2

- [x] T043 [US2] Add LIST intent mapping (show, list, what's, view) to system prompt in backend/src/agent/prompts.py
- [x] T044 [US2] Configure agent to use list_tasks tool in backend/src/agent/chat_agent.py
- [x] T045 [US2] Add confirmation templates for list results and empty list in backend/src/agent/prompts.py

**Checkpoint**: User Stories 1 and 2 complete - can create and list tasks

---

## Phase 5: User Story 3 - Complete Tasks (Priority: P2)

**Goal**: Users can mark tasks as completed by name reference

**Independent Test**: Create task, say "I finished [task]", verify completed=true

### MCP Tool for US3

- [x] T046 [US3] Implement complete_task MCP tool with user_id, task_id params in backend/src/mcp/tools/complete_task.py
- [x] T047 [US3] Add TASK_NOT_FOUND error handling in backend/src/mcp/tools/complete_task.py
- [x] T048 [US3] Add ALREADY_COMPLETED error handling in backend/src/mcp/tools/complete_task.py
- [x] T049 [US3] Register complete_task tool with MCP server in backend/src/mcp/server.py

### AI Agent Update for US3

- [x] T050 [US3] Add COMPLETE intent mapping (done, complete, finished, mark) to system prompt in backend/src/agent/prompts.py
- [x] T051 [US3] Implement tool chaining: list_tasks then complete_task for ambiguous references in backend/src/agent/chat_agent.py
- [x] T052 [US3] Add clarification logic when multiple tasks match in backend/src/agent/chat_agent.py
- [x] T053 [US3] Add confirmation template for task completion in backend/src/agent/prompts.py

**Checkpoint**: User Stories 1-3 complete - can create, list, and complete tasks

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P2)

**Goal**: Users can permanently remove tasks from their list

**Independent Test**: Create task, say "delete [task]", verify task removed from database

### MCP Tool for US4

- [x] T054 [US4] Implement delete_task MCP tool with user_id, task_id params in backend/src/mcp/tools/delete_task.py
- [x] T055 [US4] Add TASK_NOT_FOUND error handling in backend/src/mcp/tools/delete_task.py
- [x] T056 [US4] Register delete_task tool with MCP server in backend/src/mcp/server.py

### AI Agent Update for US4

- [x] T057 [US4] Add DELETE intent mapping (delete, remove, cancel, drop) to system prompt in backend/src/agent/prompts.py
- [x] T058 [US4] Implement tool chaining: list_tasks then delete_task for ambiguous references in backend/src/agent/chat_agent.py
- [x] T059 [US4] Add confirmation template for task deletion in backend/src/agent/prompts.py

**Checkpoint**: User Stories 1-4 complete - full task lifecycle except updates

---

## Phase 7: User Story 5 - Update Tasks (Priority: P3)

**Goal**: Users can modify task title or description

**Independent Test**: Create task, say "change title to [new]", verify update persisted

### MCP Tool for US5

- [x] T060 [US5] Implement update_task MCP tool with user_id, task_id, optional title, optional description in backend/src/mcp/tools/update_task.py
- [x] T061 [US5] Add TASK_NOT_FOUND error handling in backend/src/mcp/tools/update_task.py
- [x] T062 [US5] Add NO_CHANGES error when neither title nor description provided in backend/src/mcp/tools/update_task.py
- [x] T063 [US5] Ensure unchanged fields remain untouched (minimal modification) in backend/src/mcp/tools/update_task.py
- [x] T064 [US5] Register update_task tool with MCP server in backend/src/mcp/server.py

### AI Agent Update for US5

- [x] T065 [US5] Add UPDATE intent mapping (change, update, rename, edit, modify) to system prompt in backend/src/agent/prompts.py
- [x] T066 [US5] Configure agent to use update_task tool in backend/src/agent/chat_agent.py
- [x] T067 [US5] Add confirmation template for task update in backend/src/agent/prompts.py

**Checkpoint**: All task operations complete - full CRUD via chat

---

## Phase 8: User Story 6 - Conversation Continuity (Priority: P2)

**Goal**: Conversations persist across server restarts with full history

**Independent Test**: Send 3 messages, restart server, send 4th message, verify history intact

### Implementation for US6

- [x] T068 [US6] Verify message persistence stores all messages before AI call in backend/src/api/chat.py
- [x] T069 [US6] Verify history fetch loads complete conversation on each request in backend/src/api/chat.py
- [x] T070 [US6] Add conversation_id validation to prevent cross-user access in backend/src/api/chat.py
- [x] T071 [US6] Ensure no in-memory state in chat handler (stateless verification) in backend/src/api/chat.py

**Checkpoint**: Stateless architecture verified - conversations survive restarts

---

## Phase 9: User Story 7 - New Conversation (Priority: P3)

**Goal**: Users can start fresh conversations without previous context

**Independent Test**: Send message without conversation_id, verify new conversation created

### Implementation for US7

- [x] T072 [US7] Ensure new conversation created when conversation_id is None in backend/src/api/chat.py
- [x] T073 [US7] Return new conversation_id in response for client state management in backend/src/api/chat.py

**Checkpoint**: All user stories complete for backend

---

## Phase 10: Frontend - ChatKit Integration (Priority: P1)

**Goal**: Functional chat UI connected to backend API

**Independent Test**: Open frontend, type message, see response rendered

### ChatKit Implementation

- [x] T074 Create ChatInterface component wrapping ChatKit in frontend/src/components/ChatInterface.tsx
- [x] T075 Create API client for POST /api/{user_id}/chat in frontend/src/lib/api.ts
- [x] T076 Implement conversation_id state management in React in frontend/src/components/ChatInterface.tsx
- [x] T077 Create main chat page using ChatInterface in frontend/src/app/page.tsx
- [x] T078 Configure NEXT_PUBLIC_OPENAI_DOMAIN_KEY environment variable in frontend/.env.local
- [x] T079 Add "New Conversation" button that clears conversation_id in frontend/src/components/ChatInterface.tsx
- [x] T080 Configure CORS in backend to accept frontend domain in backend/src/main.py

**Checkpoint**: Frontend complete - full-stack application functional

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Error Handling Polish

- [x] T081 [P] Verify all MCP tools return proper error codes in backend/src/mcp/tools/
- [x] T082 Verify error translation covers all error codes in backend/src/utils/error_handler.py
- [x] T083 Verify no stack traces or internal errors exposed to users in backend/src/api/chat.py

### Documentation

- [x] T084 [P] Create backend README with setup instructions in backend/README.md
- [x] T085 [P] Create frontend README with setup instructions in frontend/README.md
- [x] T086 Create root README with architecture overview and quick start in README.md
- [x] T087 Add API documentation to root README in README.md
- [x] T088 Document all environment variables in .env.example files

### Deployment

- [x] T089 [P] Create Dockerfile for backend (multi-stage build) in backend/Dockerfile
- [x] T090 Update docker-compose.yml with all services in docker-compose.yml
- [x] T091 Verify docker-compose up starts full stack successfully

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phases 3-4 (US1, US2)**: Depend on Phase 2 - Core P1 stories
- **Phases 5-6 (US3, US4)**: Depend on Phase 2 - P2 stories, need list_tasks from US2
- **Phase 7 (US5)**: Depends on Phase 2 - P3 story
- **Phase 8-9 (US6, US7)**: Depend on Phases 3-4 - Conversation management
- **Phase 10 (Frontend)**: Depends on Phase 4 - Needs working API
- **Phase 11 (Polish)**: Depends on all previous phases

### User Story Dependencies

| Story | Can Start After | Dependencies on Other Stories |
|-------|-----------------|-------------------------------|
| US1 (Create) | Phase 2 | None - fully independent |
| US2 (List) | Phase 2 | None - fully independent |
| US3 (Complete) | Phase 2 | Needs list_tasks for disambiguation |
| US4 (Delete) | Phase 2 | Needs list_tasks for disambiguation |
| US5 (Update) | Phase 2 | None - fully independent |
| US6 (Continuity) | Phases 3-4 | Needs working chat flow |
| US7 (New Conv) | Phases 3-4 | Needs working chat flow |

### Parallel Opportunities

Within Phase 1 (Setup):
```
T003, T004, T005, T006, T007 can run in parallel
```

Within Phase 2 (Foundational):
```
T010, T011, T012 (models) can run in parallel
T018, T021 can run in parallel
```

Within Each User Story:
```
MCP tools can be developed in parallel with agent prompts
Multiple model files can be created in parallel
```

Across User Stories (after Phase 2):
```
US1 and US2 can run in parallel (both P1)
US3, US4, US5 can run in parallel (after US2 list_tasks exists)
```

---

## Parallel Example: Phase 2 Foundational

```bash
# Launch all model creations together:
Task: T010 "Create Task SQLModel in backend/src/models/task.py"
Task: T011 "Create Conversation SQLModel in backend/src/models/conversation.py"
Task: T012 "Create Message SQLModel in backend/src/models/message.py"

# After models, launch in parallel:
Task: T018 "Better Auth integration in backend/src/auth/better_auth.py"
Task: T021 "Health check endpoint in backend/src/api/health.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Create Tasks)
4. Complete Phase 4: User Story 2 (List Tasks)
5. Complete Phase 10: Frontend (basic integration)
6. **STOP and VALIDATE**: Can create and list tasks via chat UI
7. Deploy/demo as MVP

### Incremental Delivery

| Increment | Stories | Capability |
|-----------|---------|------------|
| MVP | US1, US2 | Create and list tasks |
| v1.1 | + US3 | Complete tasks |
| v1.2 | + US4 | Delete tasks |
| v1.3 | + US6 | Conversation persistence |
| v2.0 | + US5, US7 | Update tasks, new conversations |

### Suggested MVP Scope

**Recommended MVP**: Phases 1-4 + Phase 10

This delivers:
- Task creation via chat
- Task listing with filters
- Working frontend UI
- Stateless backend (verified by US6 later)

Total tasks for MVP: ~44 tasks

---

## Summary

| Category | Count |
|----------|-------|
| **Total Tasks** | 91 |
| Phase 1 (Setup) | 8 |
| Phase 2 (Foundational) | 16 |
| Phase 3 (US1 - Create) | 14 |
| Phase 4 (US2 - List) | 7 |
| Phase 5 (US3 - Complete) | 8 |
| Phase 6 (US4 - Delete) | 6 |
| Phase 7 (US5 - Update) | 8 |
| Phase 8 (US6 - Continuity) | 4 |
| Phase 9 (US7 - New Conv) | 2 |
| Phase 10 (Frontend) | 7 |
| Phase 11 (Polish) | 11 |

### Tasks Per User Story

| User Story | Task Count | Priority |
|------------|------------|----------|
| US1 (Create Tasks) | 14 | P1 |
| US2 (List Tasks) | 7 | P1 |
| US3 (Complete Tasks) | 8 | P2 |
| US4 (Delete Tasks) | 6 | P2 |
| US5 (Update Tasks) | 8 | P3 |
| US6 (Conversation Continuity) | 4 | P2 |
| US7 (New Conversation) | 2 | P3 |

### Parallel Opportunities Identified

- 5 parallel tasks in Phase 1 (Setup)
- 6 parallel tasks in Phase 2 (Foundational)
- Model files can be created in parallel within each story
- MCP tools and agent prompts can be developed in parallel
- After Phase 2, all P1/P2/P3 stories can theoretically run in parallel

### Format Validation

✅ ALL 91 tasks follow the checklist format:
- Checkbox prefix: `- [ ]`
- Task ID: T001-T091
- [P] marker where applicable
- [US#] label for user story phases
- File path in description

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [US#] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests are NOT included (not explicitly requested in spec)
