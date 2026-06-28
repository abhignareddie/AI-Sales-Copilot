"""Tests for the YAML Workflow Engine and Graph compilation."""

import pytest
from unittest.mock import MagicMock, patch
from app.framework.engine import WorkflowEngine
from app.framework.registry import AgentRegistry


@pytest.fixture(autouse=True)
def setup_dummy_agents():
    """Register dummy agents for test workflows."""
    @AgentRegistry.register("patient_triage_agent")
    class PatientTriage(MagicMock):
        name = "patient_triage_agent"
        async def execute(self, state):
            state.setdefault("executed_agents", [])
            state["executed_agents"].append(self.name)
            return state

    @AgentRegistry.register("symptom_analyzer_agent")
    class SymptomAnalyzer(MagicMock):
        name = "symptom_analyzer_agent"
        async def execute(self, state):
            state.setdefault("executed_agents", [])
            state["executed_agents"].append(self.name)
            return state

    @AgentRegistry.register("medical_history_agent")
    class MedicalHistory(MagicMock):
        name = "medical_history_agent"
        async def execute(self, state):
            state.setdefault("executed_agents", [])
            state["executed_agents"].append(self.name)
            return state

    @AgentRegistry.register("clinical_risk_agent")
    class ClinicalRisk(MagicMock):
        name = "clinical_risk_agent"
        async def execute(self, state):
            state.setdefault("executed_agents", [])
            state["executed_agents"].append(self.name)
            return state

    @AgentRegistry.register("treatment_recommender_agent")
    class TreatmentRecommender(MagicMock):
        name = "treatment_recommender_agent"
        async def execute(self, state):
            state.setdefault("executed_agents", [])
            state["executed_agents"].append(self.name)
            return state

    @AgentRegistry.register("medical_review_agent")
    class MedicalReview(MagicMock):
        name = "medical_review_agent"
        async def execute(self, state):
            state.setdefault("executed_agents", [])
            state["executed_agents"].append(self.name)
            return state


def test_workflow_engine_load_sales():
    """Test loading and compiling the Sales workflow from YAML config."""
    engine = WorkflowEngine("sales_copilot")
    assert engine.config["name"] == "AI Sales Copilot"
    assert engine.config["domain"] == "sales"
    assert len(engine.config["workflows"]) == 7


def test_workflow_engine_load_healthcare():
    """Test loading and compiling the Healthcare workflow from YAML config."""
    engine = WorkflowEngine("healthcare_copilot")
    assert engine.config["name"] == "Healthcare Diagnostics Copilot"
    assert engine.config["domain"] == "healthcare"
    assert len(engine.config["workflows"]) == 5


@pytest.mark.asyncio
async def test_workflow_engine_execute_healthcare():
    """Test executing the compiled healthcare workflow."""
    engine = WorkflowEngine("healthcare_copilot")
    
    # Execute the workflow
    result = await engine.execute(customer_id=101, business_goal="Triage candidate symptoms", user_id=1)
    
    assert result["execution_id"] is not None
    assert "patient_triage_agent" in result["executed_agents"]
    assert "symptom_analyzer_agent" in result["executed_agents"]
    assert "medical_history_agent" in result["executed_agents"]
    assert "clinical_risk_agent" in result["executed_agents"]
    assert "treatment_recommender_agent" in result["executed_agents"]
