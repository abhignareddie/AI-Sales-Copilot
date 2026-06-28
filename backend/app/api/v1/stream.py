import asyncio
from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse
from app.core.dependencies import get_db, get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/stream/planner")
async def stream_planner_updates(request: Request, current_user: User = Depends(get_current_user)):
    """SSE streaming route publishing real-time agent execution updates."""
    async def event_generator():
        # Step-by-step simulator events
        events = [
            {"event": "start", "message": "Planner compiled agent itinerary", "node": "planner", "time": "0.1s"},
            {"event": "agent", "message": "CRM profile fields mapped", "node": "crm", "time": "0.4s"},
            {"event": "agent", "message": "Knowledge documents search complete", "node": "knowledge", "time": "0.8s"},
            {"event": "agent", "message": "Support frustration risk scored at 90%", "node": "support", "time": "1.2s"},
            {"event": "agent", "message": "Opportunity values updated to $150K", "node": "opportunity", "time": "1.5s"},
            {"event": "complete", "message": "AI NBA generation complete", "node": "recommendation", "time": "2.1s"}
        ]
        for e in events:
            if await request.is_disconnected():
                break
            yield {
                "event": "update",
                "data": f'{{"node": "{e["node"]}", "message": "{e["message"]}", "status": "{e["event"]}", "time": "{e["time"]}"}}'
            }
            await asyncio.sleep(1.5)

    return EventSourceResponse(event_generator())
