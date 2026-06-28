# Presentation Outline — AI Sales Copilot

A structured outline for a 5-minute hackathon pitch.

---

## Slide 1: The Problem (1 minute)
- **Title**: The Enterprise AI Gap: Autonomous Failures & Hallucinations.
- **Problem**: Large language models and autonomous agents are powerful, but giving them the keys to execute B2B contract changes, send emails, or modify pricing lists without supervision is dangerous.
- **Pain Points**: Security vulnerability, SOC2 compliance failures, and business loss.

---

## Slide 2: The Solution (1 minute)
- **Title**: AI Sales Copilot: Explainable, Auditable Next Best Actions.
- **Concept**: A multi-agent framework that does not act autonomously. Every recommendation is generated with confidence scores and evidence chains, then sent to a human review queue.
- **Core Pillars**:
  1. LangGraph Multi-Agent Pipeline.
  2. Zero Trust Security (ABAC, MFA, Encryption).
  3. Explainability and Simulation.

---

## Slide 3: Live Demo Journey (2 minutes)
- **MFA Enrollment**: Show zero trust setup.
- **Graph Execution**: Run recommendation flow live, showing the agent state graph blinking and fanning-out in real-time.
- **Human Approval**: Open the queue, run a what-if simulation, add comments, and click approve.
- **PDF Report**: Download the generated ReportLab document.

---

## Slide 4: Business Case & Impact (1 minute)
- **ROI**: Demonstrable conversion uplift and risk reduction.
- **Tech Highlights**: FastAPI, React 19, TypeScript, ChromaDB, Redis, Postgres.
- **Closing**: AI Sales Copilot is secure by default, explainable by design, and production-ready today.
