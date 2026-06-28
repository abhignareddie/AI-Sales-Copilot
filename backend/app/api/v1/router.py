from fastapi import APIRouter
from app.api.v1 import auth, customers, meetings, emails, support_tickets, knowledge, recommendations, memories, users, audit_logs, dashboard, analytics, uploads, search, agent, review, memory_endpoints, security_endpoints, stream

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(security_endpoints.router, tags=["Security & Compliance"])
api_router.include_router(stream.router, tags=["Live Streaming"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(meetings.router, prefix="/meetings", tags=["Meetings"])
api_router.include_router(emails.router, prefix="/emails", tags=["Emails"])
api_router.include_router(support_tickets.router, prefix="/support-tickets", tags=["Support Tickets"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge Base"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
api_router.include_router(memories.router, prefix="/memories", tags=["Memory"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["Audit Logs"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["File Uploads"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(review.router, prefix="/review", tags=["Human-in-the-Loop Review"])
api_router.include_router(memory_endpoints.router, tags=["Enterprise Memory & Timeline"])

# Phase 3 — AI Agent routes
api_router.include_router(agent.router, tags=["AI Agents"])


