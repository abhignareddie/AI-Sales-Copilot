"""LLM Provider implementations supporting OpenAI, Gemini, Ollama, and Mock modes."""

from __future__ import annotations

import json
from typing import Optional
from app.framework.interfaces import BaseLLMProvider
from app.core.config import settings
from app.core.logging import logger


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API wrapper using LangChain ChatOpenAI."""

    def __init__(self, model: str | None = None, api_key: str | None = None):
        self.model = model or settings.OPENAI_MODEL
        self.api_key = api_key or settings.OPENAI_API_KEY

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        if not self.api_key:
            logger.warning("[OpenAIProvider] No API key configured - running mock mode fallback")
            return await MockLLMProvider().generate(prompt, system_prompt)

        from langchain_openai import ChatOpenAI
        from langchain_core.messages import SystemMessage, HumanMessage

        llm = ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            request_timeout=settings.AGENT_TIMEOUT,
        )
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        
        response = await llm.ainvoke(messages)
        return str(response.content)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API wrapper using LangChain ChatGoogleGenerativeAI."""

    def __init__(self, model: str | None = None, api_key: str | None = None):
        self.model = model or settings.GEMINI_MODEL
        self.api_key = api_key or settings.GEMINI_API_KEY

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        if not self.api_key:
            logger.warning("[GeminiProvider] No API key configured - running mock mode fallback")
            return await MockLLMProvider().generate(prompt, system_prompt)

        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import SystemMessage, HumanMessage

        llm = ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=self.api_key,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        
        response = await llm.ainvoke(messages)
        return str(response.content)


class OllamaProvider(BaseLLMProvider):
    """Local Ollama instance integration for offline or private enterprise deployments."""

    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        from langchain_community.chat_models import ChatOllama
        from langchain_core.messages import SystemMessage, HumanMessage

        llm = ChatOllama(
            base_url=self.base_url,
            model=self.model,
            temperature=temperature,
        )
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        response = await llm.ainvoke(messages)
        return str(response.content)


class MockLLMProvider(BaseLLMProvider):
    """Deterministic Mock LLM provider that simulates structured JSON responses based on prompts."""

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        # Lowercase for keyword checking
        p = prompt.lower()
        
        # 1. Planner Agent Mock
        if "planner" in (system_prompt or "").lower() or "planner_agent" in p:
            return json.dumps({
                "agents_to_call": ["crm_agent", "risk_agent", "recommendation_agent", "human_review_agent", "memory_agent"],
                "execution_order": [
                    {"step": 1, "agents": ["crm_agent"], "parallel": False},
                    {"step": 2, "agents": ["risk_agent"], "parallel": False},
                    {"step": 3, "agents": ["recommendation_agent"], "parallel": False},
                    {"step": 4, "agents": ["human_review_agent"], "parallel": False},
                    {"step": 5, "agents": ["memory_agent"], "parallel": False}
                ],
                "reasoning": "Plan compiled dynamically by Mock LLM for local demonstration.",
                "parallel_opportunities": [],
                "skipped_agents": ["transcript_agent", "email_agent", "support_agent", "knowledge_agent"]
            })

        # 2. Risk Agent Mock
        if "risk" in (system_prompt or "").lower() or "risk_agent" in p:
            return json.dumps({
                "overall_risk_score": 0.25,
                "risk_level": "low",
                "deal_risk": {"score": 0.2, "factors": ["Normal sales cycle speed"], "mitigation": []},
                "budget_risk": {"score": 0.15, "factors": ["Budget approved verbally"], "mitigation": []},
                "competitor_risk": {"score": 0.3, "factors": ["Competitor offering lower price"], "mitigation": ["Value mapping"]},
                "delay_risk": {"score": 0.2, "factors": ["Legal review timeline"], "mitigation": []},
                "churn_risk": {"score": 0.1, "factors": ["Strong relationship profile"], "mitigation": []},
                "explanation": "Low overall risk. Client is highly engaged.",
                "top_risk_factors": ["Competitor presence"],
                "recommended_actions": ["Deliver product differentiator document"]
            })

        # 3. Opportunity Agent Mock
        if "opportunity" in (system_prompt or "").lower() or "opportunity_agent" in p:
            return json.dumps({
                "overall_opportunity_score": 0.85,
                "win_probability": {"score": 0.8, "factors": ["Executive sponsor confirmed"], "blockers": []},
                "upsell_opportunity": {"score": 0.6, "products": ["Premium analytics add-on"], "reasoning": "Expressed need for custom reporting"},
                "cross_sell_opportunity": {"score": 0.4, "products": ["Support tier upgrade"], "reasoning": "Enterprise scale SLA match"},
                "renewal_chance": {"score": 0.9, "factors": ["Consistent high NPS score"]},
                "expansion_opportunity": {"score": 0.5, "areas": ["European team seats"], "reasoning": "New division expansion plan"},
                "deal_value_estimate": "$75,000",
                "next_milestone": "Security verification checklist",
                "key_strengths": ["Integrates with their existing systems"],
                "recommended_approach": "Emphasize custom analytics values"
            })

        # 4. Recommendation Agent Mock
        if "recommendation" in (system_prompt or "").lower() or "recommendation_agent" in p:
            return json.dumps({
                "recommendations": [
                    {
                        "priority": 1,
                        "action": "Schedule custom product demo focused on advanced analytics dashboards.",
                        "category": "demo",
                        "reason": "Customer needs custom reporting for division leadership.",
                        "evidence": ["transcript notes highlight reporting gap"],
                        "confidence": 0.9,
                        "expected_impact": "high",
                        "supporting_crm_data": "Pipeline stage: PROPOSAL",
                        "supporting_knowledge": "Sales Playbook Page 14 (Analytics positioning)",
                        "supporting_meetings": "Meeting on 24th June: customer asked for custom reports",
                        "supporting_emails": "Email thread: asked about custom dashboards API",
                        "why_this_recommendation": "Direct response to critical pain point.",
                        "why_alternatives_rejected": "Direct PDF reports won't satisfy their interactive needs.",
                        "timeline": "immediate"
                    },
                    {
                        "priority": 2,
                        "action": "Share security and compliance whitepaper.",
                        "category": "content",
                        "reason": "Preparing for security clearance check next week.",
                        "evidence": ["Security questionnaire deadline"],
                        "confidence": 0.85,
                        "expected_impact": "medium",
                        "supporting_crm_data": "N/A",
                        "supporting_knowledge": "Security checklist doc",
                        "supporting_meetings": "N/A",
                        "supporting_emails": "N/A",
                        "why_this_recommendation": "Clears standard roadblock in B2B buying.",
                        "why_alternatives_rejected": "Postponing would delay deal sign-off.",
                        "timeline": "this_week"
                    }
                ],
                "overall_confidence": 0.88,
                "overall_strategy": "Build technical confidence and address security requirements.",
                "evidence_summary": ["Dashboards inquiry", "Security compliance focus"]
            })

        # 5. Transcript analysis Mock
        if "transcript" in (system_prompt or "").lower() or "transcript_agent" in p:
            return json.dumps({
                "pain_points": ["Reporting flexibility", "API integration latency"],
                "budget": {"mentioned": True, "range": "$50k-$80k", "constraints": "Annual budget cap"},
                "timeline": {"urgency": "high", "deadline": "Q3 End", "notes": "Target launch August"},
                "competitors": ["Salesforce Analytics", "PowerBI"],
                "decision_makers": [{"name": "Jane", "role": "VP Analytics", "influence": "high"}],
                "sentiment": {"overall": "positive", "score": 0.85, "notes": "Customer excited about speed"},
                "action_items": ["Send API docs", "Prepare custom sandbox link"],
                "missing_information": ["Security policy document"],
                "key_quotes": ["We need this live by end of August."],
                "engagement_level": "high"
            })

        # Default text fallback
        return f"Mock response for prompt: {prompt[:100]}... [System prompt: {system_prompt}]"


class LLMFactory:
    """Helper factory class to load requested provider from system configuration."""

    @classmethod
    def get_provider(cls, provider_type: str | None = None) -> BaseLLMProvider:
        prov = provider_type or "auto"
        if prov == "auto":
            if settings.OPENAI_API_KEY:
                prov = "openai"
            elif settings.GEMINI_API_KEY:
                prov = "gemini"
            else:
                prov = "mock"

        if prov == "openai":
            return OpenAIProvider()
        elif prov == "gemini":
            return GeminiProvider()
        elif prov == "ollama":
            return OllamaProvider()
        else:
            return MockLLMProvider()
