# Healthcare Prior Authorization – Agentic AI POC

## Overview

This project is an **Agentic AI Proof of Concept (POC)** for Healthcare Prior Authorization.

The goal is to demonstrate how a controlled, evidence-grounded workflow can assist with preparing prior authorization cases for clinical review.

Instead of allowing an AI model to make an autonomous medical-necessity decision, the system uses specialized agents and deterministic application controls to:

- Select the appropriate policy and policy version
- Extract relevant clinical evidence
- Check documentation completeness
- Compare evidence against policy criteria
- Independently verify criteria results
- Prepare a structured recommendation
- Maintain an auditable workflow
- Route the case to an authorized human reviewer

> **Important Safety Boundary:**  
> The system does **not** autonomously deny or make an adverse medical-necessity decision.  
> The workflow intentionally stops at **HUMAN_REVIEW**.

---

# Business Problem

Prior Authorization requires healthcare organizations to review clinical documentation and determine whether a requested service satisfies the applicable coverage or medical-necessity criteria.

The process can involve:

- Multiple clinical documents
- Different insurance products
- Procedure-specific policies
- Policy version and effective-date validation
- Missing documentation
- Conflicting clinical evidence
- Manual evidence-to-criteria comparison
- Regulatory and audit requirements

The purpose of this POC is to reduce the manual effort required to **prepare a case for clinical review**, while keeping final clinical authority with an authorized human reviewer.

---

# Example Use Case

The current POC uses a synthetic ACL Reconstruction prior authorization request.

### Requested Service

- Procedure: ACL Reconstruction Surgery
- Procedure Code: `29888`
- Diagnosis: Anterior Cruciate Ligament Tear
- Product: `PPO-GOLD-01`

### Clinical Documentation

The synthetic case contains:

- MRI Report
- Orthopedic Consultation
- Physical Therapy Record

### Policy Criteria

The selected policy evaluates whether:

1. The ACL tear is confirmed by appropriate diagnostic imaging.
2. The patient demonstrates symptomatic instability or functional limitation.
3. Conservative treatment such as physical therapy has been attempted.
4. ACL reconstruction is recommended by an orthopedic specialist.

---

# High-Level Workflow

```text
Prior Authorization Request
            |
            v
      Policy Resolution
            |
            v
       Evidence Agent
            |
            v
     Completeness Agent
            |
            v
  Clinical Criteria Agent
            |
            v
       Verifier Agent
            |
            v
      Coordinator Agent
            |
            v
       Recommendation
            |
            v
       HUMAN_REVIEW
            |
            v
 Authorized Human Decision
```

The application owns the workflow state and determines which stage executes next.

Agents perform bounded tasks but do not control the final clinical decision.

---

# Application Architecture

The POC is organized into five logical layers.

## 1. Experience Layer

Planned reviewer interface for displaying:

- Case information
- Clinical evidence
- Policy information
- Criteria results
- Missing documentation
- Verification results
- Recommendation
- Human review controls

A Streamlit-based reviewer UI is planned.

---

## 2. Orchestration Layer

The application-owned state machine controls the workflow.

Current stages include:

```text
INTAKE
  |
  v
POLICY_RESOLUTION
  |
  v
EVIDENCE_EXTRACTION
  |
  v
COMPLETENESS_CHECK
  |
  v
CRITERIA_EVALUATION
  |
  v
VERIFICATION
  |
  v
COORDINATOR
  |
  v
HUMAN_REVIEW
```

The application — not the AI model — owns:

- Workflow state
- Execution order
- Stop conditions
- Policy selection
- Authorization boundaries
- Final action controls

---

## 3. Data Layer

The current POC uses synthetic data stored as JSON.

Examples include:

```text
data/
├── cases/
│   ├── happy_path.json
│   ├── missing_evidence.json
│   ├── conflicting_evidence.json
│   └── prompt_injection.json
│
└── policies/
    ├── acl_policy_2025.json
    └── acl_policy_2026.json
```

No production patient data is required for the POC.

---

## 4. Action Layer

The application contains a mock decision service.

Final actions are protected through deterministic guardrails.

An adverse decision requires:

- Human approval
- Reviewer identity
- Approval token

The AI workflow cannot independently perform an adverse decision.

---

## 5. Control Plane

Cross-cutting controls include:

- Audit logging
- Human-in-the-loop enforcement
- Policy version tracking
- Workflow state management
- Decision guardrails
- Regression testing

---

# Agents and Responsibilities

## Evidence Agent

### Purpose

Extract relevant clinical facts from submitted clinical documentation.

### Example

Input:

```text
MRI of the left knee demonstrates a complete anterior cruciate ligament tear.
```

Structured evidence:

```text
ACL tear confirmed
Source: MRI Report
Confidence: High
```

### Current Implementation

The current implementation uses deterministic keyword-based extraction.

Claude-based evidence extraction is planned.

---

## Policy Resolution

### Purpose

Select the appropriate governed policy using:

- Insurance product
- Procedure code
- Request date
- Policy effective date
- Policy expiration date

Example:

```text
Product Code: PPO-GOLD-01
Procedure Code: 29888
Request Date: 2026-08-31

        ↓

POL-ACL-2026
Version: 2026.1
```

Policy resolution remains deterministic and outside the AI model.

---

## Completeness Agent

### Purpose

Determine whether required documentation is available.

For the ACL policy, expected documentation includes:

- Diagnostic imaging report
- Orthopedic consultation
- Conservative treatment / physical therapy documentation

Missing documentation is reported as missing.

The system does not convert missing evidence into a negative clinical conclusion.

---

## Clinical Criteria Agent

### Purpose

Map extracted clinical evidence against individual policy criteria.

Example:

```text
ACL-001
ACL tear confirmed by diagnostic imaging

Evidence:
MRI Report

Status:
Met
```

Possible criteria states include:

```text
Met
Not demonstrated
Conflicting
Not applicable
```

The current implementation uses deterministic prototype logic.

Claude-assisted criteria reasoning is planned.

---

## Verifier Agent

### Purpose

Provide an independent validation layer.

For example, if a criterion is marked:

```text
Met
```

the verifier checks whether supporting evidence is actually attached.

A criterion should not be marked as supported without evidence.

---

## Coordinator Agent

### Purpose

Combine:

```text
Completeness Results
        +
Criteria Results
        +
Verification Results
```

and produce a review recommendation.

Possible recommendations include:

```text
Criteria appear met

More information required

Clinical review required
```

A recommendation is **not a final authorization decision**.

---

# Human-in-the-Loop Safety Boundary

Human review is a core architectural requirement.

The workflow intentionally ends at:

```text
HUMAN_REVIEW
```

The system can:

- Extract evidence
- Identify missing documentation
- Map evidence to policy criteria
- Verify criteria results
- Prepare recommendations

The system cannot autonomously:

- Deny a prior authorization
- Make an adverse medical-necessity determination
- Override a governed policy
- Modify source clinical records

---

# Decision Guardrail

The mock decision service contains deterministic controls for adverse decisions.

Conceptually:

```text
Adverse Decision Requested
          |
          v
Is Human Approved?
     /          \
   No            Yes
   |              |
 BLOCK       Approval Token?
                /      \
              No        Yes
              |          |
            BLOCK      ALLOW
```

The current autonomy-boundary tests verify that:

1. AI cannot deny without human approval.
2. A denial requires an approval token.
3. A properly human-approved action is allowed by the mock decision service.

---

# Audit Logging

The workflow records major execution events.

Current audit events include:

```text
WORKFLOW_STARTED

POLICY_SELECTED

EVIDENCE_EXTRACTED

COMPLETENESS_EVALUATED

CRITERIA_EVALUATED

VERIFICATION_COMPLETED

RECOMMENDATION_CREATED

HUMAN_REVIEW_REQUIRED
```

Audit logs are written as JSONL files under:

```text
logs/
```

General workflow telemetry is designed to avoid unnecessary sensitive clinical content.

For example, audit events can record:

- Case ID
- Workflow stage
- Event type
- Policy ID
- Policy version
- Criteria status
- Verification status
- Recommendation

while avoiding unnecessary logging of:

- Raw clinical notes
- Member name
- Date of birth

---

# Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application and workflow |
| Pydantic | Structured data models and validation |
| Application State Machine | Workflow orchestration and stop conditions |
| JSON | Synthetic cases and policy corpus |
| Pytest | Automated testing |
| JSONL | Audit logging |
| python-dotenv | Environment configuration |
| Git / GitHub | Source control and collaboration |
| Claude API | Planned bounded AI reasoning |
| Streamlit | Planned reviewer interface |

---

# Project Structure

```text
healthcare-prior-auth/
│
├── README.md
├── requirements.txt
├── pytest.ini
├── .env.example
├── .gitignore
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── agents/
│   │   ├── evidence_agent.py
│   │   ├── policy_agent.py
│   │   ├── completeness_agent.py
│   │   ├── criteria_agent.py
│   │   ├── verifier_agent.py
│   │   └── coordinator_agent.py
│   │
│   ├── models/
│   │   ├── case.py
│   │   ├── evidence.py
│   │   ├── policy.py
│   │   └── workflow_state.py
│   │
│   ├── workflow/
│   │   ├── graph.py
│   │   ├── routing.py
│   │   └── guardrails.py
│   │
│   ├── services/
│   │   ├── policy_service.py
│   │   ├── decision_service.py
│   │   └── audit_service.py
│   │
│   └── prompts/
│
├── data/
│   ├── cases/
│   ├── clinical_documents/
│   └── policies/
│
├── tests/
│   ├── test_policy_version.py
│   ├── test_missing_evidence.py
│   ├── test_conflicting_evidence.py
│   ├── test_prompt_injection.py
│   └── test_autonomy_boundary.py
│
├── ui/
│   └── streamlit_app.py
│
└── logs/
```

---

# Current Implementation Status

The following components are currently implemented:

- Project structure
- Python virtual environment
- Synthetic ACL prior authorization case
- Versioned ACL policy
- Pydantic case models
- Deterministic policy resolution
- Evidence extraction prototype
- Documentation completeness checking
- Clinical criteria evaluation prototype
- Independent verifier
- Coordinator
- Human-review guardrail
- Mock decision service
- Audit logging
- Application-owned state machine
- Happy-path end-to-end execution
- Autonomy-boundary tests

---

# Current Happy-Path Result

The current synthetic case is:

```text
Case ID: PA-ACL-1001
```

The workflow selects:

```text
Policy: POL-ACL-2026
Version: 2026.1
```

Criteria evaluation:

```text
ACL-001 → Met
ACL-002 → Met
ACL-003 → Met
ACL-004 → Met
```

Verification:

```text
Verification Passed: True
```

Coordinator recommendation:

```text
Criteria appear met
```

Final workflow state:

```text
HUMAN_REVIEW
```

Therefore:

```text
Criteria appear met ≠ Automatically Approved
```

The authorized human reviewer retains final decision authority.

---

# Setup

## Prerequisites

Recommended:

```text
Python 3.12+
Git
VS Code
```

---

## Clone the Repository

Fork the repository first, then clone your fork:

```bash
git clone https://github.com/<YOUR_USERNAME>/healthcare-prior-auth-agentic-ai.git
```

Move into the project:

```bash
cd healthcare-prior-auth-agentic-ai
```

---

# Create Virtual Environment

### Windows PowerShell

```powershell
python -m venv .venv
```

Activate:

```powershell
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Run the Application

From the project root:

```bash
python -m app.main
```

The application will load the synthetic happy-path case and execute the prior authorization workflow.

Expected final state:

```text
Current Stage: HUMAN_REVIEW
Human Review Required: True
```

---

# Run Tests

Run:

```bash
pytest
```

Or:

```bash
pytest -v
```

The autonomy-boundary tests verify that adverse decisions cannot bypass the required human approval controls.

---

# Environment Variables

Copy:

```text
.env.example
```

to:

```text
.env
```

Do not commit `.env`.

The `.gitignore` should exclude:

```text
.env
.venv/
__pycache__/
*.pyc
.pytest_cache/
logs/
```

When Claude integration is added, environment variables will include values such as:

```text
ANTHROPIC_API_KEY=<your-api-key>
ANTHROPIC_MODEL=<approved-model-name>
```

Never commit API keys to GitHub.

---

# Team Development

Create a separate branch for each feature.

Examples:

```bash
git checkout -b feature/negative-scenarios
```

```bash
git checkout -b feature/claude-integration
```

```bash
git checkout -b feature/patient-dataset
```

```bash
git checkout -b feature/streamlit-ui
```

```bash
git checkout -b feature/testing
```

After making changes:

```bash
git add .
git commit -m "Describe your change"
git push origin <branch-name>
```

Then create a Pull Request for review before merging into `main`.

---

# Planned Enhancements

The next implementation phases are:

1. Negative scenario testing
   - Missing evidence
   - Conflicting evidence
   - Prompt injection
   - Incorrect / expired policy version

2. Claude integration
   - Clinical evidence understanding
   - Structured evidence extraction
   - Evidence-to-policy reasoning
   - Structured outputs
   - Prompt-injection resistance

3. Synthetic patient dataset
   - Multiple prior authorization cases
   - Batch workflow execution
   - Case-level metrics
   - Safety and workflow statistics

4. Reviewer UI
   - Streamlit interface
   - Case queue
   - Evidence display
   - Policy criteria matrix
   - Recommendation
   - Human review controls

5. Evaluation
   - Happy-path regression
   - Missing evidence
   - Conflicting evidence
   - Policy mismatch
   - Prompt injection
   - Human-approval enforcement

6. Final demonstration
   - Intake
   - Policy resolution
   - Evidence extraction
   - Completeness
   - Criteria evaluation
   - Verification
   - Recommendation
   - Human review

---

# Future Dataset Workflow

The POC can be extended from a single case to a synthetic patient/case dataset.

```text
Synthetic Prior Authorization Dataset
                 |
                 v
             Case Loader
                 |
                 v
        Application State Machine
                 |
        +--------+---------+
        |        |         |
        v        v         v
      Case 1   Case 2    Case N
        |        |         |
        v        v         v
       Agentic Workflow Execution
                 |
                 v
          Aggregate Results
                 |
                 v
        Reviewer Dashboard
```

This will allow the POC to demonstrate behavior across different case types instead of only one happy-path example.

---

# Key Design Principle

The core principle of this POC is:

> **AI prepares the case. The authorized human owns the final clinical decision.**

The objective is not to replace clinical judgment.

The objective is to make prior authorization review more:

- Structured
- Evidence-grounded
- Explainable
- Auditable
- Consistent
- Efficient
- Safe

---

# Disclaimer

This repository is a proof of concept using synthetic data.

It is not intended for production clinical decision-making and should not be used to make real patient coverage or medical-necessity decisions without appropriate healthcare, security, privacy, compliance, clinical, and regulatory review.