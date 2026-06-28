import yaml
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from app.core.logging import logger

DEFAULT_RULES = """
rules:
  - name: "Low Customer Health Escalation"
    condition: "customer.health_score < 50"
    action: "Recommend immediate follow-up call with customer"
    priority: "high"
    category: "escalation"
    roi_estimate: 2500.0

  - name: "Large Deal VP Review"
    condition: "customer.annual_revenue > 100000 or customer.company_size > 1000"
    action: "Recommend manager/VP review of opportunity strategy"
    priority: "critical"
    category: "proposal"
    roi_estimate: 15000.0

  - name: "Competitor Risk Demo"
    condition: "competitor_detected == True"
    action: "Recommend scheduling technical demo highlighting differentiators"
    priority: "high"
    category: "demo"
    roi_estimate: 8000.0

  - name: "Support Ticket Escalation"
    condition: "support_tickets_count > 5"
    action: "Recommend customer success check-in call to address open tickets"
    priority: "high"
    category: "follow_up"
    roi_estimate: 4500.0
"""

class BusinessRuleEngine:
    """Evaluates business rules over customer data."""
    
    def __init__(self, rule_yaml: str = DEFAULT_RULES):
        try:
            self.config = yaml.safe_load(rule_yaml)
            self.rules = self.config.get("rules", [])
        except Exception as e:
            logger.error(f"Failed to load rule configuration: {e}")
            self.rules = []

    def evaluate(self, customer_data: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate rules and generate matching recommendations."""
        matches = []
        
        # Build evaluation sandbox namespace
        eval_namespace = {
            "customer": type("CustomerObject", (object,), customer_data)(),
            "competitor_detected": context.get("competitor_detected", False),
            "support_tickets_count": context.get("support_tickets_count", 0),
        }
        
        # Ensure properties on customer object exist dynamically
        for k, v in customer_data.items():
            setattr(eval_namespace["customer"], k, v)
            
        for rule in self.rules:
            condition = rule.get("condition", "False")
            try:
                # Safe evaluation
                if eval(condition, {"__builtins__": None}, eval_namespace):
                    matches.append({
                        "title": rule.get("name"),
                        "action": rule.get("action"),
                        "priority": rule.get("priority", "medium"),
                        "category": rule.get("category", "other"),
                        "estimated_roi": rule.get("roi_estimate", 0.0),
                        "evidence": f"Rule match: '{rule.get('name')}' condition '{condition}' was met."
                    })
            except Exception as e:
                logger.warning(f"Error evaluating rule '{rule.get('name')}': {e}")
                
        return matches

class RiskAnalysisEngine:
    """Calculates risk levels and explains risk scores (0-100)."""
    
    def calculate(self, customer: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        # Extract properties
        health = customer.get("health_score", 50.0)
        stage = customer.get("current_stage", "prospect")
        tickets = context.get("support_tickets_count", 0)
        competitor = context.get("competitor_detected", False)
        
        # Calculate sub-scores
        deal_risk = 100.0 - health
        budget_risk = 40.0 if stage in ("negotiation", "closed_lost") else 15.0
        competitor_risk = 80.0 if competitor else 20.0
        technical_risk = 30.0 + (10.0 * min(5, tickets))
        timeline_risk = 50.0 if stage == "proposal" else 25.0
        adoption_risk = 80.0 - health
        support_risk = min(100.0, tickets * 15.0)
        churn_risk = 100.0 - health + (tickets * 5.0)
        
        scores = {
            "deal_risk": min(100.0, max(0.0, deal_risk)),
            "budget_risk": budget_risk,
            "competitor_risk": competitor_risk,
            "technical_risk": min(100.0, technical_risk),
            "timeline_risk": timeline_risk,
            "adoption_risk": min(100.0, max(0.0, adoption_risk)),
            "support_risk": support_risk,
            "churn_risk": min(100.0, max(0.0, churn_risk)),
        }
        
        overall = sum(scores.values()) / len(scores)
        
        explanations = []
        if overall > 60:
            explanations.append("Overall risk is HIGH due to competitor activity or high number of support tickets.")
        else:
            explanations.append("Overall risk is MODERATE; maintain steady engagement and resolve pending support tickets.")
            
        if competitor:
            explanations.append("Competitor detected in correspondence, increasing competitor risk.")
            
        if tickets > 3:
            explanations.append(f"Customer has {tickets} open support tickets, driving support/adoption risks.")
            
        return {
            "score": round(overall, 1),
            "breakdown": scores,
            "explanations": explanations
        }

class OpportunityAnalysisEngine:
    """Calculates potential deals and expansions."""
    
    def calculate(self, customer: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        health = customer.get("health_score", 50.0)
        revenue = customer.get("annual_revenue", 10000.0)
        stage = customer.get("current_stage", "prospect")
        
        # Win Probability based on stage & health
        stage_base = {
            "prospect": 10.0,
            "qualified": 30.0,
            "proposal": 60.0,
            "negotiation": 80.0,
            "closed_won": 100.0,
            "closed_lost": 0.0
        }.get(stage, 20.0)
        
        win_prob = stage_base * 0.7 + (health * 0.3)
        win_prob = min(100.0, max(0.0, win_prob))
        
        upsell = 20.0 + (health * 0.5) if revenue < 50000 else 10.0
        cross_sell = 30.0 + (health * 0.4)
        renewal = health
        expansion = health * 0.8
        
        revenue_impact = revenue * (win_prob / 100.0)
        
        return {
            "win_probability": round(win_prob, 1),
            "upsell_opportunity": round(upsell, 1),
            "cross_sell_opportunity": round(cross_sell, 1),
            "renewal_chance": round(renewal, 1),
            "expansion_opportunity": round(expansion, 1),
            "revenue_impact": round(revenue_impact, 2)
        }

class ConfidenceEngine:
    """Scores how confident the engine is in its recommendations."""
    
    def calculate(
        self, 
        crm_completeness: float, 
        knowledge_similarity: float, 
        meeting_quality: float, 
        email_consistency: float
    ) -> Tuple[float, str]:
        # Weighted calculation
        confidence = (
            crm_completeness * 0.3 + 
            knowledge_similarity * 0.3 + 
            meeting_quality * 0.2 + 
            email_consistency * 0.2
        )
        
        explanation = f"Confidence score ({confidence:.1%}) is composed of: " \
                      f"CRM data completeness ({crm_completeness:.0%}), " \
                      f"Knowledge search similarity ({knowledge_similarity:.0%}), " \
                      f"Meeting transcript depth ({meeting_quality:.0%}), and " \
                      f"Email sentiment consistency ({email_consistency:.0%})."
                      
        return round(confidence, 2), explanation

class ExplainabilityEngine:
    """Explains why specific choices were made and why others were rejected."""
    
    def explain(
        self, 
        action: str, 
        evidence: List[str], 
        docs: List[str], 
        meetings: List[str], 
        crm_fields: List[str], 
        alternatives: List[str]
    ) -> Dict[str, Any]:
        return {
            "why_this_action": f"Recommended '{action}' because of direct evidence from {', '.join(crm_fields)} matching standard business policies.",
            "evidence_details": evidence,
            "supporting_knowledge_docs": docs,
            "supporting_meetings": meetings,
            "supporting_crm_fields": crm_fields,
            "rejected_alternatives_rationale": f"Alternatives like {', '.join(alternatives)} were rejected as they do not directly mitigate immediate risk or carry lower projected ROI."
        }

class WhatIfSimulator:
    """Simulates business decisions and estimates their ROI and Win Probability changes."""
    
    def simulate(self, customer: Dict[str, Any], parameter: str, value: Any) -> Dict[str, Any]:
        health = customer.get("health_score", 50.0)
        revenue = customer.get("annual_revenue", 10000.0)
        stage = customer.get("current_stage", "prospect")
        
        stage_base = {
            "prospect": 15.0,
            "qualified": 35.0,
            "proposal": 65.0,
            "negotiation": 85.0
        }.get(stage, 20.0)
        
        original_prob = stage_base * 0.7 + (health * 0.3)
        original_prob = min(100.0, max(0.0, original_prob))
        
        simulated_prob = original_prob
        roi = 0.0
        impact = "Neutral"
        explanation = ""
        
        if parameter == "discount":
            discount = float(value)
            # Higher discount increases win prob but lowers net revenue impact
            prob_bump = min(20.0, discount * 0.8)
            simulated_prob = min(98.0, original_prob + prob_bump)
            net_revenue = revenue * (1 - (discount / 100.0))
            roi = (net_revenue * (simulated_prob / 100.0)) - (revenue * (original_prob / 100.0))
            impact = "Positive" if roi > 0 else "Negative"
            explanation = f"Increasing discount to {discount}% increases win probability by {prob_bump:.1f}%, resulting in simulated probability of {simulated_prob:.1f}%. Projected net revenue change is ${roi:,.2f}."
            
        elif parameter == "delay_weeks":
            delay = int(value)
            # Delaying reduces win probability
            prob_drop = delay * 5.0
            simulated_prob = max(5.0, original_prob - prob_drop)
            roi = - (revenue * (prob_drop / 100.0))
            impact = "Negative"
            explanation = f"Delaying the demo/proposal by {delay} week(s) drops win probability by {prob_drop}%, resulting in simulated probability of {simulated_prob:.1f}%. Lost revenue risk is estimated at ${abs(roi):,.2f}."
            
        else:
            explanation = f"Parameter {parameter} is not supported for simulation."
            
        return {
            "customer_id": customer.get("id", 0),
            "parameter": parameter,
            "original_value": "standard" if parameter == "discount" else 0,
            "simulated_value": value,
            "original_probability": round(original_prob / 100.0, 3),
            "simulated_probability": round(simulated_prob / 100.0, 3),
            "estimated_roi": round(roi, 2),
            "business_impact": impact,
            "explanation": explanation
        }
