import pytest
from app.services.decision_engine import (
    BusinessRuleEngine,
    RiskAnalysisEngine,
    OpportunityAnalysisEngine,
    ConfidenceEngine,
    ExplainabilityEngine,
    WhatIfSimulator
)

@pytest.fixture
def mock_customer():
    return {
        "id": 1,
        "company_name": "Acme Corp",
        "current_stage": "proposal",
        "health_score": 45.0,
        "annual_revenue": 150000.0,
        "company_size": 1200,
    }

def test_business_rules(mock_customer):
    engine = BusinessRuleEngine()
    context = {
        "competitor_detected": True,
        "support_tickets_count": 6
    }
    
    recs = engine.evaluate(mock_customer, context)
    
    # Verify matches
    actions = [r["action"] for r in recs]
    assert any("immediate follow-up" in a for a in actions) # Health < 50
    assert any("manager/VP review" in a for a in actions)    # Revenue > 100k
    assert any("technical demo" in a for a in actions)       # Competitor detected
    assert any("customer success check-in" in a for a in actions) # Tickets > 5

def test_risk_analysis(mock_customer):
    engine = RiskAnalysisEngine()
    context = {
        "competitor_detected": True,
        "support_tickets_count": 3
    }
    
    res = engine.calculate(mock_customer, context)
    assert "score" in res
    assert res["score"] > 0
    assert "competitor_risk" in res["breakdown"]
    assert res["breakdown"]["competitor_risk"] == 80.0

def test_opportunity_analysis(mock_customer):
    engine = OpportunityAnalysisEngine()
    context = {}
    
    res = engine.calculate(mock_customer, context)
    assert "win_probability" in res
    assert "revenue_impact" in res
    assert res["upsell_opportunity"] > 0

def test_confidence_engine():
    engine = ConfidenceEngine()
    score, explanation = engine.calculate(
        crm_completeness=0.8,
        knowledge_similarity=0.7,
        meeting_quality=0.9,
        email_consistency=0.85
    )
    assert 0.0 <= score <= 1.0
    assert "Confidence score" in explanation

def test_explainability_engine():
    engine = ExplainabilityEngine()
    res = engine.explain(
        action="Schedule Demo",
        evidence=["Competitor detected"],
        docs=["competitor_comparison.pdf"],
        meetings=["Sync Call"],
        crm_fields=["health_score"],
        alternatives=["Discount proposal"]
    )
    assert "why_this_action" in res
    assert "rejected_alternatives_rationale" in res

def test_what_if_simulator(mock_customer):
    engine = WhatIfSimulator()
    
    # Test discount simulation
    res_discount = engine.simulate(mock_customer, "discount", 15.0)
    assert res_discount["simulated_probability"] >= res_discount["original_probability"]
    assert res_discount["business_impact"] in ("Positive", "Negative")
    
    # Test delay simulation
    res_delay = engine.simulate(mock_customer, "delay_weeks", 2)
    assert res_delay["simulated_probability"] <= res_delay["original_probability"]
