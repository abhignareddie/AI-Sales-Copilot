# Demo Walkthrough Guide — AI Sales Copilot

This guide outlines the step-by-step walkthrough to demonstrate the core value of the platform during a live presentation.

---

## The Demo Walkthrough Journey

### Step 1: Zero Trust Login & MFA Setup
1. Log in to the application and navigate to the **Security Console**.
2. Click **Generate TOTP Secret**. This will register a new multi-factor authentication token.
3. Verify verification code checking using your Google Authenticator app.

### Step 2: Ingest Customer Inbound Signals
1. Navigate to the **Knowledge Center**.
2. Click the Upload Zone and upload `premium_pricing_plan.pdf`.
3. The system parses, splits, and indexes the document into ChromaDB.

### Step 3: Run the Live Recommendation Flow
1. Navigate to the **AI Copilot Flow** page.
2. Click **Run Recommendation Flow**.
3. Real-time updates stream down the SSE channel.
4. The visual agent graph shows active highlights: CRM Agent, RAG Search, Risk Agent, etc.

### Step 4: Human-in-the-Loop Review
1. Navigate to the **Review Queue**.
2. Find the generated recommendation: *"Schedule immediate VP proposal alignment review"*.
3. Read the supporting evidence, confidence score, and projected ROI.
4. Click **Approve & Execute**. The state changes immediately and appends to the immutable audit logs.
5. Launch the **What-If Deal Simulator** to recalculate win probabilities dynamically.

### Step 5: Export Executive Report
1. Navigate to the **BI Analytics** page.
2. Click **Export PDF Report**.
3. This downloads a styled executive report detailing next steps and account statuses.
