import pytest
from datetime import datetime, timezone
from app.services.hitl_service import ApprovalWorkflowEngine, NotificationService
from app.services.memory_service import MemoryManager, LearningEngine

@pytest.fixture
def mock_approvals():
    return [
        {"role": "sales_rep", "action": "approved"},
        {"role": "sales_manager", "action": "approved"}
    ]

def test_determine_approval_chain():
    # Large deal -> sequential
    rule1 = ApprovalWorkflowEngine.determine_approval_chain(120000.0, 30.0)
    assert rule1["type"] == "sequential"
    assert "director" in rule1["roles"]
    
    # High risk -> single manager
    rule2 = ApprovalWorkflowEngine.determine_approval_chain(50000.0, 75.0)
    assert rule2["type"] == "single"
    assert "sales_manager" in rule2["roles"]
    
    # Standard -> single sales_rep
    rule3 = ApprovalWorkflowEngine.determine_approval_chain(10000.0, 10.0)
    assert rule3["type"] == "single"
    assert "sales_rep" in rule3["roles"]

def test_evaluate_votes(mock_approvals):
    # Rule matching sequential roles
    rule = {
        "type": "sequential",
        "roles": ["sales_rep", "sales_manager"],
        "votes_required": 2
    }
    
    status = ApprovalWorkflowEngine.evaluate_votes(mock_approvals, rule)
    assert status == "approved"
    
    # Test rejection override
    mock_approvals_with_rej = mock_approvals + [{"role": "director", "action": "rejected"}]
    status_rej = ApprovalWorkflowEngine.evaluate_votes(mock_approvals_with_rej, rule)
    assert status_rej == "rejected"

def test_learning_engine_adjust_rankings():
    recs = [
        {"action": "Email discount code", "confidence": 0.5},
        {"action": "Offer technical product demo", "confidence": 0.6}
    ]
    
    past_approvals = [
        {"recommendation": "Offer technical product demo to developer team"}
    ]
    past_rejections = [
        {"recommendation": "Email discount code to prospect"}
    ]
    
    adjusted = LearningEngine.adjust_rankings(recs, past_approvals, past_rejections)
    
    # "Offer technical product demo" should have confidence boosted
    # "Email discount code" should be penalized
    demo_rec = [r for r in adjusted if "technical product demo" in r["action"].lower()][0]
    email_rec = [r for r in adjusted if "email discount" in r["action"].lower()][0]
    
    assert demo_rec["confidence"] > 0.6
    assert email_rec["confidence"] < 0.5
