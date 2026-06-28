# Deployment Guide — AI Sales Copilot

Production deployment guide for the AI Sales Copilot platform. The application is packaged using Docker and orchestrated using Docker Compose.

---

## Production Architecture Diagram

```
Internet --> Nginx (Reverse Proxy :80/:443)
               |
               +---> frontend (Nginx Webserver :3000)
               |
               +---> backend (FastAPI :8000)
                       |
                       +---> postgres (Database :5432)
                       |
                       +---> redis (Session Store :6379)
                       |
                       +---> chromadb (Vector Store :8000)
```

---

## 1. Prerequisites
- Docker (version 20.10 or later)
- Docker Compose (version 2.20 or later)
- Fully configured `.env` file containing secrets, connection URIs, and LLM provider details.

---

## 2. Docker Compose Configuration
The `docker-compose.yml` file defines 5 primary services:
1. **`backend`**: FastAPI application server.
2. **`frontend`**: Vite static files served via Nginx.
3. **`postgres`**: Permanent relational storage.
4. **`redis`**: Cache and session registry.
5. **`chromadb`**: Vector store for hybrid semantic RAG searches.

To build and start all services:
```bash
docker-compose up --build -d
```

---

## 3. Environment Variables (`.env`)
Ensure the following variables are customized in production:

```ini
# Core Configuration
DEBUG=false
SECRET_KEY=use-a-strong-random-hex-key-here
ALGORITHM=HS256

# Database Connection
DATABASE_URL=postgresql+asyncpg://postgres:secure_password@postgres:5432/ai_sales_copilot

# Redis Cache URL
REDIS_URL=redis://redis:6379/0

# ChromaDB Client
CHROMA_HOST=chromadb
CHROMA_PORT=8000

# LLM Providers Configuration
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
```

---

## 4. Health Checks & Verification
Each service includes automated Docker health checks:
- **FastAPI Backend**: `curl http://localhost:8000/health` (Checks database connection, Redis, and ChromaDB availability).
- **Postgres**: Checks if postgres database accepts socket connections.
- **Redis**: Pings the redis server.
