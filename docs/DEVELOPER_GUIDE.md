# Developer Guide — AI Sales Copilot

This guide helps developers get started with building, running, and modifying the AI Sales Copilot platform.

---

## Codebase Architecture

The project is structured into clean separation of concerns:
1. **Presentation Layer (`frontend/src/`)**: Single-page application built on React 19, TypeScript, TailwindCSS, and React Flow.
2. **API Router Layer (`backend/app/api/v1/`)**: Handles validation (Pydantic), routing (FastAPI), security filters (ABAC), and Server-Sent Events (SSE).
3. **Database Layer (`backend/app/models/` and `backend/app/repositories/`)**: Implements async SQLAlchemy mappings and the generic Repository Pattern.
4. **AI/ML Layer (`backend/app/agents/`)**: Multi-agent StateGraph pipeline built on LangGraph.

---

## Local Setup

### 1. Python Environment Setup
Use Python 3.11:
```bash
cd backend
python -m venv .venv
.venv/Scripts/activate          # Windows
source .venv/bin/activate       # macOS/Linux
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 2. Database Initialization
Ensure a local PostgreSQL and Redis instance are running. Modify `.env` as required, then run:
```bash
# Run database migrations using Alembic (if configured)
# or run the application directly which automatically builds tables in debug mode.
```

### 3. Start Backend Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 4. Start Frontend Development Server
```bash
cd frontend
npm install
npm run dev
```
The frontend will run at: `http://localhost:3000`.

---

## Core Development Guidelines

### Adding new API endpoints
1. Define the response/request schemas in `backend/app/schemas/`.
2. Create or modify the router file in `backend/app/api/v1/`.
3. Include the router in the global `api_router` inside `backend/app/api/v1/router.py`.

### Modifying LangGraph Agent Nodes
1. Agent stubs are located in `backend/app/agents/`.
2. The core orchestration assembly happens in `backend/app/agents/graph/langgraph_builder.py`.
3. State parameters are defined inside `backend/app/agents/schemas/agent_state.py`.

---

## Testing

Ensure all tests pass before making pull requests:
```bash
cd backend
.venv/Scripts/python -m pytest tests/ -v
```
To run only security checks:
```bash
.venv/Scripts/python -m pytest tests/test_security_governance.py -v
```
