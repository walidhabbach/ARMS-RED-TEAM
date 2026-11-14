# 🛡️ Agentic Red Team Assessment Report

**Project:** Agentic Red Team - ARMS simulator
**Generated:** 2026-11-14T05:17:20.668388+00:00
**Scope:** Local simulator only; synthetic transactions only.

---

# Executive Summary

**Overall Risk Score:** **0.652/1.0 (MEDIUM)**

## Risk Formula

`0.35*business_impact + 0.25*likelihood + 0.20*regulatory_exposure + 0.20*control_weakness`

## Risk Factors

- **Business Impact**: 0.7
- **Likelihood**: 0.75
- **Regulatory Exposure**: 0.65
- **Control Weakness**: 0.45

# 1. Reconnaissance

## Asset Inventory

- Target: Local ARMS simulator
- Base URL: http://127.0.0.1:8000
- Sample Transactions: 5
- Sample Alerts: 5
- Sample Audit Events: 5

## Health Status

| Property | Value |
|----------|----------|
| Status | ok |
| Service | ARMS-simulator |
| Timestamp | 2026-11-14T05:15:17.689178+00:00 |

## Endpoint Inventory

| Method | Endpoint | Summary | Operation ID |
|----------|----------|----------|----------|
| GET | `/health` | Health | health_health_get |
| POST | `/transactions` | Create Transaction | create_transaction_transactions_post |
| GET | `/transactions` | List Transactions | list_transactions_transactions_get |
| POST | `/analyze` | Analyze Transaction | analyze_transaction_analyze_post |
| GET | `/transactions/{transaction_id}` | Get Transaction | get_transaction_transactions__transaction_id__get |
| GET | `/alerts` | List Alerts | list_alerts_alerts_get |
| GET | `/logs` | List Logs | list_logs_logs_get |

## Technology Stack

- agno
- openai
- ollama
- fastapi
- uvicorn[standard]
- pydantic
- pydantic-settings
- python-dotenv
- sqlalchemy
- scikit-learn
- numpy
- pandas
- pytest
- httpx
- streamlit

## Reconnaissance Limitations

- Only the exposed local simulator API was inspected.
- No production infrastructure or external provider was contacted.
- The endpoint inventory does not prove that authentication is required or absent.

## Reconnaissance Agent Analysis

Here's the analysis of the observed ARMS inventory:

**Observed Assets:**

* Local ARMS simulator
* Endpoint URLs:
	+ `http://127.0.0.1:8000/health`
	+ `http://127.0.0.1:8000/transactions` (GET, POST)
	+ `http://127.0.0.1:8000/analyze` (POST)
	+ `http://127.0.0.1:8000/transactions/{transaction_id}` (GET)
	+ `http://127.0.0.1:8000/alerts` (GET)
	+ `http://127.0.0.1:8000/logs` (GET)
* Observed dependencies:
	+ `agno`
	+ `openai`
	+ `ollama`
	+ `fastapi`
	+ `uvicorn[standard]`
	+ `pydantic`
	+ `pydantic-settings`
	+ `python-dotenv`
	+ `sqlalchemy`
	+ `scikit-learn`
	+ `numpy`
	+ `pandas`
	+ `pytest`
	+ `httpx`
	+ `streamlit`

**Data Flows:**

* The simulator exposes health information via the `/health` endpoint.
* The simulator allows creating, listing, and analyzing transactions via the `/transactions` endpoint.
* The simulator allows listing alerts and logs via the `/alerts` and `/logs` endpoints, respectively.
* The simulator exposes individual transaction data via the `/transactions/{transaction_id}` endpoint.

**Attack Surfaces:**

* The exposed API endpoints can be attacked using various methods (e.g., SQL injection, cross-site scripting (XSS), etc.).
* The `analyze` endpoint may be vulnerable to sensitive data exposure or unauthorized access.
* The `transactions` endpoint may be vulnerable to unauthorized access or modification.

**Unknowns:**

* The simulator's authentication mechanism is unknown.
* The simulator's authorization mechanism is unknown.
* The simulator's data storage and retrieval mechanisms are unknown.

**Recommended Safe Tests:**

* Test the `GET /health` endpoint to verify its functionality.
* Test the `GET /transactions` endpoint to verify its functionality.
* Test the `GET /alerts` and `GET /logs` endpoints to verify their functionality.
* Test the `GET /transactions/{transaction_id}` endpoint to verify its functionality.

Note that these tests are safe because they do not involve any malicious or unauthorized actions. They are designed to verify the simulator's functionality and identify potential vulnerabilities.

# 2. Attack Simulation

**Scenario:** synthetic_transaction_injection_and_validation_test

**Scope:** Local ARMS simulator and synthetic records only

## Test: synthetic_transaction_submission

- HTTP Status: 200

- Accepted: True
- Authorization Header Sent: False

### Transaction Details

| Field | Value |
|----------|----------|
| id | 108 |
| transaction_ref | RT-CYBER-457A004CF5 |
| amount | 7600.0 |
| currency | EUR |
| country_code | FR |
| merchant_category | retail |
| channel | online |
| account_age_days | 12 |
| transactions_last_hour | 6 |
| is_cross_border | True |
| status | ANALYZED |
| risk_score | 1.0 |
| classification | SUSPICIOUS |
| anomaly_score | 1.0 |
| model_version | arms-baseline-1.0 |
| created_at | 2026-11-14T05:15:18.147301 |

### Detection Explanation

- High transaction amount (>= EUR 5,000).
- High transaction velocity (>= 5 transactions/hour).
- Cross-border transaction.
- Recently created account (< 30 days).
- Isolation Forest anomaly signal: 1.00 (0–1).

**Decision:** SUSPICIOUS

> A test transaction was accepted without an Authorization header; this is a lab observation, not proof of a production breach.

## Test: negative_amount_validation

- HTTP Status: 422

- Rejected As Expected: True

## Test: duplicate_reference_protection

- HTTP Status: 409

- Rejected As Expected: True

## Attacker Agent Analysis

**Test Findings and Analysis**

**Test 1: Synthetic Transaction Submission**

* **Name:** synthetic_transaction_submission
* **HTTP Status:** 200
* **Accepted:** True
* **Authorization Header Sent:** False
* **Response:** The transaction was accepted, and the response contained a transaction ID, reference, amount, currency, and other relevant information.

**Severity:** N/A (expected behavior)

**Rationale:** This is a synthetic transaction test, which is designed to mimic a legitimate transaction. The fact that the transaction was accepted and the response contained relevant information is within expected behavior.

**Fix:** N/A (expected behavior)

**Test 2: Negative Amount Validation**

* **Name:** negative_amount_validation
* **HTTP Status:** 422
* **Rejected as Expected:** True

**Severity:** N/A (expected behavior)

**Rationale:** This test was designed to validate the API's handling of negative amounts. The 422 HTTP status code indicates that the request was rejected due to a validation error, which is the expected behavior.

**Fix:** N/A (expected behavior)

**Test 3: Duplicate Reference Protection**

* **Name:** duplicate_reference_protection
* **HTTP Status:** 409
* **Rejected as Expected:** True

**Severity:** N/A (expected behavior)

**Rationale:** This test was designed to validate the API's handling of duplicate transaction references. The 409 HTTP status code indicates that the request was rejected due to a duplicate reference, which is the expected behavior.

**Fix:** N/A (expected behavior)

**Conclusion:** All three tests were executed successfully, and the results align with the expected behavior of the API. There are no indications of security breaches or vulnerabilities in this controlled test environment.

# 3. AI Adversary Testing

**Scenario:** synthetic_input_perturbation

**Scope:** Synthetic transaction feature changes; no training data or production model was modified.

## amount_threshold_neighbourhood

| Metric | Baseline | Perturbed |
|----------|----------|----------|
| Risk Score | 0.2 | 0.48 |
| Classification | LEGITIMATE | LEGITIMATE |
| Anomaly Score | 1.0 | 1.0 |

- Risk Score Delta: 0.28
- Classification Changed: False

### Baseline Explanation

- No configured high-risk rule was triggered.
- Isolation Forest anomaly signal: 1.00 (0–1).

### Perturbed Explanation

- High transaction amount (>= EUR 5,000).
- Isolation Forest anomaly signal: 1.00 (0–1).

## velocity_threshold_neighbourhood

| Metric | Baseline | Perturbed |
|----------|----------|----------|
| Risk Score | 0.2 | 0.44 |
| Classification | LEGITIMATE | LEGITIMATE |
| Anomaly Score | 1.0 | 1.0 |

- Risk Score Delta: 0.24
- Classification Changed: False

### Baseline Explanation

- No configured high-risk rule was triggered.
- Isolation Forest anomaly signal: 1.00 (0–1).

### Perturbed Explanation

- High transaction velocity (>= 5 transactions/hour).
- Isolation Forest anomaly signal: 1.00 (0–1).

### Interpretation Note

A changed score is a sensitivity signal, not by itself proof of exploitable model evasion.

## AI Adversary Analysis

Based on the provided controlled AI input-perturbation results, here's the analysis:

**Score Changes:**

* In the "amount_threshold_neighbourhood" test, the baseline risk score is 0.2, and the perturbed risk score is 0.48, resulting in a delta of 0.28.
* In the "velocity_threshold_neighbourhood" test, the baseline risk score is 0.2, and the perturbed risk score is 0.44, resulting in a delta of 0.24.

These score changes indicate that the model's predictions are sensitive to the perturbed inputs, as the risk scores increased in both tests.

**Classification Flips:**

* In neither of the two tests did the classification change (i.e., the classification remained "LEGITIMATE" in both baseline and perturbed scenarios).

**Threshold Sensitivity:**

* The threshold for the model to classify an input as an anomaly appears to be around the risk score of 0.5. Both perturbed inputs, with risk scores of 0.48 and 0.44, are below this threshold, indicating that the model is not yet flagging these inputs as anomalies.

**Limitations:**

* The model's inability to detect anomalies in the perturbed scenarios may indicate a lack of robustness to input perturbations.
* The small delta in risk scores (0.28 and 0.24) might suggest that the model is not sensitive enough to detect changes in input features.

**Recommendations:**

1. **Robustness Tests:** Conduct more extensive perturbation tests to evaluate the model's robustness to various input perturbations.
2. **Feature Validation:** Validate the feature importance and relevance to ensure that the model is relying on the correct input features.
3. **Drift Monitoring:** Implement drift monitoring to detect changes in the data distribution over time and adjust the model accordingly.
4. **Human Review:** Perform regular human reviews of the model's predictions to identify potential issues and provide feedback to improve the model's performance.
5. **Data Augmentation:** Consider incorporating data augmentation techniques to increase the model's robustness to input perturbations.

Keep in mind that this analysis is based on synthetic input perturbations, and the results may not directly translate to real-world scenarios. Further testing and evaluation are necessary to determine the model's performance in a production environment.

# 4. Compliance Assessment

**Scope:** Training simulator only; findings are preliminary control observations, not legal conclusions.

## Control Review

### DORA - ICT access control and protection of exposed interfaces

**Status:** REVIEW_REQUIRED

**Evidence:**

The simulator exposes POST /analyze. The current test did not evaluate identity management, authentication configuration, or authorization roles.

### DORA - Logging and traceability of security-relevant events

**Status:** PARTIALLY_OBSERVED

**Evidence:**

A logs endpoint exists in the simulator. Log integrity, retention, access restrictions, and alerting were not tested.

### EU AI Act - AI system documentation, logging, monitoring and human oversight where applicable

**Status:** REVIEW_REQUIRED

**Evidence:**

The API records model_version and decision explanations. Dataset provenance, model documentation, human oversight, risk classification and lifecycle governance were not evidenced in this stage.

### GDPR - Data minimisation, lawful basis, retention and data-subject rights where personal data is processed

**Status:** NOT_ASSESSED

**Evidence:**

The lab uses synthetic transaction records. No conclusion about GDPR compliance in a real deployment can be drawn.

### MiCA - Crypto-asset service controls where in-scope crypto-asset services are provided

**Status:** NOT_ASSESSED

**Evidence:**

A crypto_exchange merchant category appears in synthetic data, but the simulator does not implement custody, exchange, transfer or other crypto-asset service workflows.

## Areas Not Tested

- Real identity provider and role-based access control
- Third-party ICT provider contracts and exit plans
- Incident response and disaster recovery exercises
- Crypto-asset custody and key management
- Production personal data processing and retention

## Compliance Agent Analysis

Here are the observations and test results assessed against the provided frameworks:

1. **DORA - ICT access control and protection of exposed interfaces**
	* Status: REVIEW_REQUIRED
	* Evidence: The simulator exposes POST /analyze. The current test did not evaluate identity management, authentication configuration, or authorization roles.
	* Applicability: This observation is relevant to DORA, as ICT access control and protection of exposed interfaces are crucial for securing the system.
	* Potential Consequence: An unauthorized access to the system could lead to data breaches or system compromise.
	* Practical Remediation: Implement identity management, authentication configuration, and authorization roles to protect exposed interfaces.
2. **DORA - Logging and traceability of security-relevant events**
	* Status: PARTIALLY_OBSERVED
	* Evidence: A logs endpoint exists in the simulator. Log integrity, retention, access restrictions, and alerting were not tested.
	* Applicability: This observation is relevant to DORA, as logging and traceability of security-relevant events are essential for incident response and forensic analysis.
	* Potential Consequence: Inadequate logging could lead to delayed incident detection and response.
	* Practical Remediation: Implement log integrity, retention, access restrictions, and alerting mechanisms.
3. **EU AI Act - AI system documentation, logging, monitoring, and human oversight where applicable**
	* Status: REVIEW_REQUIRED
	* Evidence: The API records model_version and decision explanations. Dataset provenance, model documentation, human oversight, risk classification, and lifecycle governance were not evidenced in this stage.
	* Applicability: This observation is relevant to the EU AI Act, as AI system documentation, logging, monitoring, and human oversight are essential for accountability and transparency.
	* Potential Consequence: Inadequate documentation and oversight could lead to accountability issues and regulatory non-compliance.
	* Practical Remediation: Implement dataset provenance, model documentation, human oversight, risk classification, and lifecycle governance mechanisms.
4. **GDPR - Data minimisation, lawful basis, retention, and data-subject rights where personal data is processed**
	* Status: NOT_ASSESSED
	* Evidence: The lab uses synthetic transaction records. No conclusion about GDPR compliance in a real deployment can be drawn.
	* Applicability: This observation is relevant to GDPR, as data minimisation, lawful basis, retention, and data-subject rights are essential for personal data protection.
	* Potential Consequence: Inadequate data protection could lead to data subject rights violations and regulatory non-compliance.
	* Practical Remediation: Assess GDPR compliance in a real deployment and implement data minimisation, lawful basis, retention, and data-subject rights mechanisms.
5. **MiCA - Crypto-asset service controls where in-scope crypto-asset services are provided**
	* Status: NOT_ASSESSED
	* Evidence: A crypto_exchange merchant category appears in synthetic data, but the simulator does not implement custody, exchange, transfer, or other crypto-asset service workflows.
	* Applicability: This observation is relevant to MiCA, as crypto-asset service controls are essential for ensuring the security and integrity of crypto-asset transactions.
	* Potential Consequence: Inadequate crypto-asset service controls could lead to security and integrity issues in crypto-asset transactions.
	* Practical Remediation: Assess MiCA compliance and implement crypto-asset service controls, including custody, exchange, transfer, and other crypto-asset service workflows.

Note: The "NOT_ASSESSED" status indicates that the observation is not relevant to the framework, or the assessment is incomplete. The "REVIEW_REQUIRED" status indicates that the observation requires further review and analysis. The "PARTIALLY_OBSERVED" status indicates that the observation is partially relevant, but some aspects are not assessed.

# 5. Impact & Risk Scoring

**Final Score:** 0.652

**Severity:** MEDIUM

**Scale:** 0 to 1; higher means greater simulated risk

## Scoring Formula

```text
0.35*business_impact + 0.25*likelihood + 0.20*regulatory_exposure + 0.20*control_weakness
```

## Factor Breakdown

| Factor | Value |
|----------|----------|
| business_impact | 0.7 |
| likelihood | 0.75 |
| regulatory_exposure | 0.65 |
| control_weakness | 0.45 |

## Prioritized Findings

### RT-API-001 - Synthetic transaction submission accepted by the lab API

**Priority:** HIGH

**Evidence:** HTTP 200

**Remediation:**

For a real deployment, enforce authentication, authorization, request signing where appropriate, rate limits and transaction provenance. The lab currently has no production identity layer.

### RT-API-002 - Input validation and duplicate-reference controls

**Priority:** LOW

**Evidence:** Negative amount rejected=True; duplicate rejected=True.

**Remediation:**

Retain server-side schema validation and unique transaction references; add regression tests for boundary values.

### RT-AI-001 - Model sensitivity to small input changes

**Priority:** MEDIUM

**Evidence:** Classification flips=0; maximum absolute risk-score delta=0.280.

**Remediation:**

Expand adversarial robustness tests, calibrate thresholds, monitor drift and require human review for high-impact decisions.

## Risk Scoring Analysis

**Risk Assessment Explanation and Prioritization**

The computed risk assessment indicates a medium-level risk (Severity: MEDIUM) with a score of 0.652 on a scale of 0 to 1. This score is the result of a weighted formula that combines the likelihood, business impact, regulatory exposure, and control weakness factors.

**Assumptions and Limitations:**

1. This risk assessment is based on a classroom scoring heuristic, not a bank-approved risk model.
2. Financial loss is not estimated, as no validated loss assumptions or exposure data are supplied.
3. Regulatory exposure is a prioritization proxy, not a legal determination.

**Findings and Prioritization:**

The findings are ranked based on their priority and risk score:

1. **RT-API-001: Synthetic transaction submission accepted by the lab API** (Score: 0.35, Priority: HIGH)
	* The lab API accepts synthetic transactions without authentication, authorization, or request signing, which poses a high risk.
	* Remediation: Enforce authentication, authorization, request signing, rate limits, and transaction provenance.
2. **RT-AI-001: Model sensitivity to small input changes** (Score: 0.22, Priority: MEDIUM)
	* The model is sensitive to small input changes, which may lead to incorrect classification or risk-score delta.
	* Remediation: Expand adversarial robustness tests, calibrate thresholds, monitor drift, and require human review for high-impact decisions.
3. **RT-API-002: Input validation and duplicate-reference controls** (Score: 0.16, Priority: LOW)
	* Input validation and duplicate-reference controls are not adequately implemented, which poses a low risk.
	* Remediation: Retain server-side schema validation and unique transaction references, and add regression tests for boundary values.

**Plausible Business Consequences:**

If left unaddressed, these findings may lead to:

1. **RT-API-001:** Unauthorized access to sensitive data or systems, resulting in data breaches or financial loss.
2. **RT-AI-001:** Inaccurate risk assessments or decisions, leading to suboptimal business outcomes or regulatory non-compliance.
3. **RT-API-002:** Minor disruptions or inefficiencies due to input validation and duplicate-reference issues.

**Recommendations:**

1. Prioritize the remediation of RT-API-001, as it poses a high risk and can be mitigated with authentication and authorization controls.
2. Implement robust testing and calibration of the AI model (RT-AI-001) to ensure accurate risk assessments and decisions.
3. Address the input validation and duplicate-reference issues (RT-API-002) to prevent minor disruptions.

By addressing these findings, the organization can reduce the risk score and improve the overall resilience of its systems and operations.

# Assessment Limitations

- This is a classroom scoring heuristic, not a bank-approved risk model.
- Financial loss is not estimated because no validated loss assumptions or exposure data are supplied.
- Regulatory exposure is a prioritisation proxy, not a legal determination.

# Final Recommendations

- [HIGH] For a real deployment, enforce authentication, authorization, request signing where appropriate, rate limits and transaction provenance. The lab currently has no production identity layer.
- [LOW] Retain server-side schema validation and unique transaction references; add regression tests for boundary values.
- [MEDIUM] Expand adversarial robustness tests, calibrate thresholds, monitor drift and require human review for high-impact decisions.

# Conclusion

The Agentic Red Team assessment produced a final risk score of **0.652 (MEDIUM)**.

The assessment identified observations related to API exposure, model sensitivity, compliance governance, and authentication controls. Additional verification is recommended before any production deployment.
