import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.core.logging import logger

class NotificationService:
    """Delivers alerts for critical review events in-app, via email or webhook."""
    
    @staticmethod
    async def notify(event: str, message: str, user_id: Optional[int] = None, webhook_url: Optional[str] = None):
        logger.info(f"[Notification] [{event}] Message: {message} | Targeted User: {user_id}")
        # Webhook Delivery Simulation
        if webhook_url:
            logger.info(f"[Webhook] Sent payload to {webhook_url}")
            
class ApprovalWorkflowEngine:
    """Orchestrates configurable multi-level approvals and voting schemes."""
    
    @classmethod
    def determine_approval_chain(cls, deal_value: float, risk_score: float) -> Dict[str, Any]:
        """Configurable rules: decides type of approval and required roles."""
        if deal_value >= 100000.0:
            return {
                "type": "sequential",
                "roles": ["sales_manager", "director"],
                "votes_required": 2,
                "description": "VP and Director sequential review for large enterprise deals."
            }
        if risk_score >= 60.0:
            return {
                "type": "single",
                "roles": ["sales_manager"],
                "votes_required": 1,
                "description": "Manager review required due to high deal risk."
            }
        # Standard flow
        return {
            "type": "single",
            "roles": ["sales_rep"],
            "votes_required": 1,
            "description": "Standard representative approval."
        }

    @classmethod
    def evaluate_votes(cls, approvals: List[Dict[str, Any]], rule: Dict[str, Any]) -> str:
        """Evaluates votes based on flow rules."""
        workflow_type = rule.get("type", "single")
        required_votes = rule.get("votes_required", 1)
        
        approved_votes = [a for a in approvals if a.get("action") == "approved"]
        rejected_votes = [a for a in approvals if a.get("action") == "rejected"]
        
        if any(a.get("action") == "rejected" for a in approvals):
            return "rejected"
            
        if workflow_type == "sequential":
            # Must match exact role order
            required_roles = rule.get("roles", [])
            voted_roles = [a.get("role") for a in approved_votes]
            # Simple check if all required roles voted approved
            if all(role in voted_roles for role in required_roles):
                return "approved"
            return "pending_review"
            
        if workflow_type == "parallel" or workflow_type == "majority_voting":
            # Majority voting
            if len(approved_votes) >= required_votes:
                return "approved"
            if len(rejected_votes) >= required_votes:
                return "rejected"
            return "pending_review"
            
        # Single
        if len(approved_votes) >= 1:
            return "approved"
            
        return "pending_review"
