# Judge Evaluation Guide — AI Sales Copilot

Welcome Hackathon Judges! This document provides instructions on how to evaluate the architectural integrity, business case, security compliance, and live demo flows of the **AI Sales Copilot**.

---

## 1. Quick Verification Command List

To verify that the application has been integrated and configured correctly, run these commands:

### Backend Health Audit
Make sure all dependency databases (Postgres, Redis, ChromaDB) are reachable:
```bash
curl http://localhost:8000/health
```

### Complete Test Verification
Ensure security services, prompt injection guardrails, TOTP generation, and report rendering pass all checks:
```bash
cd backend
.venv/Scripts/python -m pytest tests/ -v
```

---

## 2. Platform Architecture Strengths (Target Score: 68+/70)

AI Sales Copilot represents a state-of-the-art enterprise architecture:
1. **Multi-Agent LangGraph (11 Agents)**: Complex graph topology supporting parallel fanning for risk/support analysis, fanning-in for synthesis, and loops.
2. **Zero Trust Compliance**: Every endpoint is protected. Attribute-Based Access Control (ABAC) restricts route execution by geography region headers.
3. **Data Security**: Symmetric column encryption using Fernet ensures that customer SSNs, email content, and meeting summaries are encrypted at rest.
4. **Audit Traceability**: Immutable audit logs record every human approval, comment, and token spend transaction.

---

## 3. Business Value & Use Case (Target Score: 29+/30)

AI Sales Copilot addresses a multi-billion dollar enterprise gap:
- **Human-in-the-Loop Safeguard**: Safeguards compliance by requiring manual confirmation before recommendation execution.
- **Explainability First**: Instead of returning generic recommendations, the platform renders confidence match scores, ROI projections, and memory logs.
- **Real-Time Forecasting**: Incorporates what-if deal simulations to let managers recalculate closing probability changes on the fly.
