---
id: 003
title: Todo AI Chatbot Implementation Plan
stage: plan
date: 2026-01-06
surface: agent
model: claude-opus-4-5-20251101
feature: 001-todo-ai-chatbot
branch: master
user: system
command: /sp.plan
labels: ["implementation-plan", "architecture", "stateless", "mcp", "fastapi", "phases"]
links:
  spec: specs/001-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-todo-ai-chatbot/plan.md
  - history/prompts/001-todo-ai-chatbot/003-todo-ai-chatbot-implementation-plan.plan.prompt.md
tests:
  - null
---

## Prompt

/sp.plan

You are Spec-Kit Plus.

Your task is to generate a clear, step-by-step IMPLEMENTATION PLAN
for building a Todo AI Chatbot using a stateless architecture and MCP tools.

Do NOT generate code.
Generate a structured execution plan only.

====================================
PROJECT GOAL
====================================

Build an AI-powered Todo Chatbot that allows users to manage tasks
(create, list, update, complete, delete) using natural language.

The system must use:
- OpenAI Agents SDK for AI logic
- MCP (Model Context Protocol) for task tools
- FastAPI backend
- SQLModel ORM
- Neon Serverless PostgreSQL
- OpenAI ChatKit frontend
- Better Auth for authentication

====================================
NON-NEGOTIABLE RULES
====================================

1. Backend server must be 100% STATELESS
2. AI agent must NEVER access database directly
3. All task operations MUST go through MCP tools
4. Conversation state must be stored in the database
5. Server restarts must NOT break conversations

[Prompt included 8 execution phases with detailed requirements for database, MCP server, AI agent, chat API, frontend, error handling, testing, and documentation]

## Response snapshot

Created comprehensive 8-phase implementation plan:

**Phase 1: Database & Persistence**
- SQLModel definitions for Task, Conversation, Message
- Neon PostgreSQL connection with async engine
- Alembic migrations with indexes

**Phase 2: MCP Server & Tools**
- Official MCP SDK setup
- 5 stateless tools: add_task, list_tasks, complete_task, delete_task, update_task
- User isolation enforcement (user_id required on all tools)
- No state storage in MCP server

**Phase 3: AI Agent Layer**
- OpenAI Agent as decision-maker only
- Intent classification with tool mapping
- Tool chaining for ambiguous requests
- Confirmation message templates

**Phase 4: Stateless Chat API**
- POST /api/{user_id}/chat endpoint
- 10-step request flow: authenticate → load history → store message → invoke AI → store response
- Conversation resumption after restart

**Phase 5: Frontend (ChatKit)**
- Environment configuration with domain key
- conversation_id state management
- API client integration

**Phase 6: Error Handling & UX**
- Error translation layer (internal → user-friendly)
- Confirmation patterns for all operations
- Never expose technical details

**Phase 7: Testing & Validation**
- Stateless validation tests
- MCP tool correctness tests
- Agent intent classification tests
- End-to-end scenarios

**Phase 8: Documentation & Deployment**
- Repository structure
- README requirements
- Docker and docker-compose artifacts
- Environment variable documentation

## Outcome

- Impact: Complete implementation roadmap for stateless Todo AI Chatbot
- Tests: Testing strategy defined across 4 categories
- Files: specs/001-todo-ai-chatbot/plan.md
- Next prompts: Run /sp.tasks to generate detailed task breakdown
- Reflection: Plan covers all architectural concerns with clear phase dependencies

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (planning document)
- Prompt variant (if applicable): Standard implementation planning
- Next experiment (smallest change to try): Validate phase dependencies with actual development timeline
