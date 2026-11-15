# 🛡️ Agentic Red Team – ARMS (Agentic Risk Monitoring System)

A classroom cybersecurity and AI governance project that implements a synthetic banking risk-monitoring platform and an Agentic Red Team framework for resilience, fraud detection, compliance assessment, and risk evaluation.

The project combines:

- A FastAPI-based transaction monitoring API
- A synthetic transaction database
- Rule-based and machine-learning fraud detection
- Audit logging and alerting
- Five specialist Agno agents
- Deterministic risk scoring
- Regulatory evidence mapping
- Synthetic robustness evaluation
- Interactive Streamlit dashboard

> This project is strictly educational and operates only on synthetic data in a controlled local environment.

---

# Project Objectives

The platform simulates how a modern financial institution could:

- Monitor transactions and fraud indicators
- Detect anomalous behavior
- Evaluate AI model robustness
- Assess compliance readiness
- Perform controlled Red Team exercises
- Prioritize remediation efforts through risk scoring

---

# Safety Scope

The project is intentionally restricted to a local laboratory environment.

- Only synthetic transactions are generated.
- Only local APIs are assessed.
- No real customer information is used.
- No real banking systems are accessed.
- No external targets are scanned.
- No production infrastructure is tested.
- Reconnaissance activities use read-only requests.
- Attack simulations use controlled synthetic API requests.

Default target:

```text
http://127.0.0.1:8000
```

---

# Architecture

```text
                      ┌──────────────────┐
                      │ ARMS Simulator   │
                      │ FastAPI + SQLite │
                      └─────────┬────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          │                     │                     │
          ▼                     ▼                     ▼
 ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
 │ Reconnaissance │  │   Attacker     │  │ AI Adversary   │
 └────────┬───────┘  └────────┬───────┘  └────────┬───────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                              ▼
                  ┌─────────────────────────┐
                  │ Compliance Breaker      │
                  └────────────┬────────────┘
                               │
                               ▼
                  ┌─────────────────────────┐
                  │ Impact & Risk Scoring   │
                  └────────────┬────────────┘
                               │
                               ▼
                      JSON & Markdown Reports
                               │
                               ▼
                      Streamlit Dashboard
```
---
## Five agents

1. **Reconnaissance:** inventories the local API surface and visible dependencies using read-only requests.
2. **Attacker:** tests controlled synthetic transaction submission, server-side validation, and duplicate-reference protection.
3. **AI Adversary:** compares fraud model outputs before and after small synthetic feature changes. This is input perturbation, not data poisoning.
4. **Compliance Breaker:** maps observed evidence to preliminary DORA, MiCA, EU AI Act and GDPR control observations. It does not make legal determinations.
5. **Impact & Risk Scoring:** calculates a reproducible 0–1 risk heuristic and prioritizes findings. It does not invent financial loss amounts.

> The Python orchestrator owns the deterministic execution order and passes evidence objects between agents. Agno agents provide specialist analysis of those evidence objects.
---

# Features

## Transaction Monitoring

- Transaction ingestion API
- Transaction retrieval API
- Alert generation
- Audit logging

## Fraud Detection

- Rule-based controls
- Threshold scoring
- Anomaly detection using Isolation Forest
- Decision explanations

## Red Team Framework

### Reconnaissance Agent

Collects:

- API health information
- OpenAPI specifications
- Endpoint inventory
- Service dependencies
- Alert statistics
- Audit statistics

### Attacker Agent

Performs controlled simulations:

- Synthetic transaction submission
- Input validation verification
- Duplicate-reference testing

### AI Adversary Agent

Evaluates model sensitivity through:

- Controlled perturbations
- Threshold-neighborhood tests
- Baseline versus modified comparisons
- Classification stability analysis

### Compliance Breaker Agent

Maps evidence against:

- DORA
- GDPR
- EU AI Act
- MiCA

and produces evidence-based control observations.

### Impact & Risk Scoring Agent

Calculates:

- Deterministic risk score
- Risk prioritization
- Findings ranking
- Remediation recommendations

---

# Requirements

Recommended:

- Python 3.11+
- SQLite
- FastAPI
- SQLAlchemy
- Scikit-Learn
- Streamlit
- Agno

For LLM-backed agent analysis:

- OpenRouter
or
- Ollama

---

# Installation

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

### Windows

```powershell
.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Configuration

Create a `.env` file:

```env
ARMS_BASE_URL=http://127.0.0.1:8000
ARMS_HTTP_TIMEOUT=8

LLM_PROVIDER=ollama

OLLAMA_MODEL=llama3.1:8b
OLLAMA_HOST=http://localhost:11434
```

or

```env
LLM_PROVIDER=openrouter

OPENROUTER_API_KEY=your_api_key
OPENROUTER_MODEL=openai/gpt-4o-mini
```

---

# Ollama Setup

Start Ollama:

```bash
ollama serve
```

Download a model:

```bash
ollama pull llama3.1:8b
```

---

# Initialize Synthetic Data

```bash
python -m arms.seed
```

This generates the synthetic baseline dataset.

---

# Start the API

```bash
python main.py
```

Available endpoints:

| Method | Endpoint |
|----------|----------|
| GET | `/health` |
| POST | `/transactions` |
| POST | `/analyze` |
| GET | `/transactions` |
| GET | `/transactions/{id}` |
| GET | `/alerts` |
| GET | `/logs` |

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

---

# Run Red Team Assessment

Deterministic execution only:

```bash
python -m orchestration.red_team --simulate-only
```

This performs:

- Reconnaissance
- Attack simulations
- AI perturbation tests
- Compliance mapping
- Risk scoring

without calling an LLM.

---

Full execution with agents:

```bash
python -m orchestration.red_team
```

This enriches collected evidence using the configured LLM provider.

---

# Generated Reports

Execution produces:

```text
reports/
├── red_team_report.json
└── red_team_report.md
```

The reports contain:

- Asset inventory
- Endpoint inventory
- Attack evidence
- AI robustness analysis
- Compliance observations
- Risk assessment
- Findings
- Recommendations
- Limitations

---

# Dashboard

Launch Streamlit:

```bash
python -m streamlit run dashboard/app.py
```

The dashboard visualizes:

- Global risk score
- Findings
- Agent outputs
- Compliance matrix
- Robustness evaluation
- Scenario catalog
- Risk trends

---

# Automated Tests

Run all tests:

```bash
python -m pytest -q
```

Tests cover:

- API functionality
- Fraud analysis
- Risk scoring
- Evaluation metrics
- Regulatory mapping
- Red Team orchestration

---

# Evaluation Metrics

The project provides synthetic evaluation metrics including:

- Precision
- Recall
- Pass rate
- Threshold sensitivity
- Classification stability
- Robustness observations

These metrics are generated using synthetic datasets and serve educational purposes only.

---

# Regulatory Coverage

The project includes evidence-oriented mappings for:

## DORA

- ICT risk management
- Logging and monitoring
- Access control

## GDPR

- Data minimization
- Retention
- Data-subject rights

## EU AI Act

- Documentation
- Monitoring
- Human oversight
- Traceability

## MiCA

- Crypto-asset service controls
- Applicability assessment

---

# Important Limitations

- Synthetic data is used exclusively.
- Results are educational and non-production.
- Fraud scores are not calibrated probabilities.
- Regulatory observations are not legal conclusions.
- Compliance mappings are not certifications.
- Threshold flips are not automatically vulnerabilities.
- Input perturbations are not data-poisoning attacks.
- A successful synthetic request is not proof of a real-world breach.
- Financial-loss estimates are intentionally excluded.
- MiCA applicability cannot be inferred from synthetic merchant categories.
- GDPR compliance cannot be determined from synthetic-only datasets.

---

# Disclaimer

This project is a teaching and experimentation platform designed to demonstrate concepts related to:

- AI governance
- Fraud detection
- Agentic systems
- Red Teaming
- Regulatory traceability
- Risk management

It must not be considered a production-ready banking system, cybersecurity assessment, or compliance certification tool.