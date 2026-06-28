import json
from typing import Dict, Any, List, Optional
from datetime import datetime

class ContextBuilder:
    """Enterprise context assembler merging multi-source business context before LLM queries."""

    @staticmethod
    def build_full_context(
        customer_data: Dict[str, Any],
        meetings: List[Dict[str, Any]],
        emails: List[Dict[str, Any]],
        support_tickets: List[Dict[str, Any]],
        memories: List[Dict[str, Any]],
        knowledge_docs: List[Dict[str, Any]],
        business_rules: List[Dict[str, Any]],
        timeline: List[Dict[str, Any]]
    ) -> str:
        """Merge all relevant telemetry, rules, and communication logs into a unified string context."""
        
        context_parts = []
        
        # 1. Customer General Telemetry
        context_parts.append("=== CUSTOMER TELEMETRY ===")
        context_parts.append(json.dumps(customer_data, indent=2))
        
        # 2. Communication logs (Meetings & Emails)
        context_parts.append("\n=== RECENT MEETINGS ===")
        if meetings:
            for idx, m in enumerate(meetings[:3]):
                date_str = m.get("meeting_date", "")
                context_parts.append(f"Meeting #{idx+1} ({date_str}): {m.get('title')} - Summary: {m.get('summary')}")
        else:
            context_parts.append("No meetings recorded.")

        context_parts.append("\n=== RECENT EMAILS ===")
        if emails:
            for idx, e in enumerate(emails[:5]):
                context_parts.append(f"Email #{idx+1}: {e.get('subject')} (Sender: {e.get('sender')} -> Receiver: {e.get('receiver')})")
        else:
            context_parts.append("No emails recorded.")
            
        # 3. Support Tickets & Escalation risk
        context_parts.append("\n=== SUPPORT TICKETS ===")
        if support_tickets:
            for idx, t in enumerate(support_tickets):
                context_parts.append(f"Ticket #{t.get('ticket_number')} [{t.get('priority')}]: {t.get('issue')} (Status: {t.get('status')})")
        else:
            context_parts.append("No open support tickets.")
            
        # 4. Long Term Memory Timeline
        context_parts.append("\n=== ACCOUNT MEMORY & TIMELINE ===")
        if timeline:
            for item in timeline:
                context_parts.append(f"[{item.get('timestamp')}]: {item.get('title')} ({item.get('type')})")
        else:
            context_parts.append("No timeline memory events recorded.")
            
        # 5. Playbooks / Knowledge matches
        context_parts.append("\n=== PLAYBOOK & KNOWLEDGE MATCHES ===")
        if knowledge_docs:
            for doc in knowledge_docs:
                context_parts.append(f"Document: {doc.get('title')} ({doc.get('document_type')}) - Match Score: {doc.get('match_score')}%")
        else:
            context_parts.append("No playbook documents matched.")
            
        # 6. Active Business Rules
        context_parts.append("\n=== TRIGGERED BUSINESS RULES ===")
        if business_rules:
            for rule in business_rules:
                context_parts.append(f"- Rule: {rule.get('title')} (Condition: {rule.get('evidence')})")
        else:
            context_parts.append("No custom business rules triggered.")
            
        return "\n".join(context_parts)
