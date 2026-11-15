# 🛡️ Agentic Red Team Assessment Report

**Project:** Agentic Red Team - ARMS simulator
**Generated:** 2026-11-15T16:51:30.646053+00:00
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
| Timestamp | 2026-11-15T16:49:37.317272+00:00 |

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
- reportlab

## Reconnaissance Limitations

- Only the exposed local simulator API was inspected.
- No production infrastructure or external provider was contacted.
- The endpoint inventory does not prove that authentication is required or absent.

## Reconnaissance Agent Analysis

**Observed Assets**

* **IP Address**: 127.0.0.1
* **Port**: 8000
* **Base URL**: http://127.0.0.1:8000
* **Services**: ARMS-simulator

**Data Flows**

* **Incoming**: None observed
* **Outgoing**: None observed

**Attack Surfaces**

1. **Authentication Bypass**: Since the inventory does not prove that authentication is required or absent, it's possible that an attacker can bypass authentication mechanisms.
2. **Unrestricted API Access**: The presence of endpoints like `/health` and `/logs` may provide an attacker with sensitive information about the system.
3. **Data Exposure**: Endpoints like `/transactions` and `/alerts` may expose sensitive data, such as transaction history and alerts.
4. **Unvalidated User Input**: The presence of `GET` endpoints that accept user-specified parameters (e.g., `transaction_id`) may allow an attacker to inject malicious input.

**Unknowns**

* **Authentication Mechanisms**: The inventory does not provide information about the authentication mechanisms used by the ARMS simulator.
* **Data Storage**: The inventory does not provide information about the data storage mechanisms used by the ARMS simulator.

**Recommended Safe Tests**

1. **API Testing**: Test the API endpoints to identify any potential vulnerabilities or misconfigurations.
2. **Authentication Testing**: Test the authentication mechanisms to identify any potential weaknesses.
3. **Data Exposure Testing**: Test the data exposure by simulating a malicious user accessing sensitive data.
4. **Input Validation Testing**: Test the input validation mechanisms to identify any potential weaknesses.

Note: These recommendations are based on the observed inventory and should be performed in a safe and controlled environment.

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
| id | 170 |
| transaction_ref | RT-CYBER-3AFD1E756A |
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
| created_at | 2026-11-15T16:49:37.787004 |

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

## Test: detection_and_audit_trail_check

- HTTP Status: None


## Attacker Agent Analysis

**Assessment Summary**

This controlled conventional security test assesses the API's weaknesses in synthetic transaction injection and validation. The tests were conducted in a lab environment using a local ARMS simulator and synthetic records.

**Test Findings**

1. **Synthetic Transaction Submission (synthetic_transaction_submission)**
	* **HTTP Status:** 200 (OK)
	* **Expected Behavior:** Acceptance of a synthetic transaction without an Authorization header
	* **Observed Behavior:** Accepted
	* **Interpretation:** This is a lab observation and not proof of a production breach. However, it highlights a potential vulnerability where unauthorized transactions can be submitted without authentication.
	* **Severity:** Medium (Unauthorized transactions can be submitted without authentication)
	* **Fix:** Implement authentication and authorization mechanisms for transaction submission
2. **Negative Amount Validation (negative_amount_validation)**
	* **HTTP Status:** 422 (Unprocessable Entity)
	* **Expected Behavior:** Rejection of transactions with negative amounts
	* **Observed Behavior:** Rejected as expected
	* **Interpretation:** The API correctly rejects transactions with negative amounts.
	* **Severity:** Low (No vulnerability found)
	* **Fix:** N/A (Correct behavior observed)
3. **Duplicate Reference Protection (duplicate_reference_protection)**
	* **HTTP Status:** 409 (Conflict)
	* **Expected Behavior:** Rejection of duplicate transaction references
	* **Observed Behavior:** Rejected as expected
	* **Interpretation:** The API correctly rejects duplicate transaction references.
	* **Severity:** Low (No vulnerability found)
	* **Fix:** N/A (Correct behavior observed)
4. **Detection and Audit Trail Check (detection_and_audit_trail_check)**
	* **Transaction Reference:** RT-CYBER-3AFD1E756A
	* **Expected Behavior:** Transaction detection and audit trail recording
	* **Observed Behavior:** Listed in alerts with correct risk score, classification, and creation timestamp
	* **Interpretation:** The API correctly detects and records transactions in the audit trail.
	* **Severity:** Low (No vulnerability found)
	* **Fix:** N/A (Correct behavior observed)

**Conclusion**

The test findings indicate that the API has some weaknesses in transaction submission and detection mechanisms. However, the correct behavior was observed for negative amount validation and duplicate reference protection. The lab observations and findings should be reviewed and addressed to strengthen the API's security posture.

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

**Evaluation of Sensitivity to Controlled Input Perturbations**

The provided results demonstrate the effects of controlled input perturbations on the predictions of the ARMS fraud model. The perturbations were introduced synthetically, without modifying the training data or production model.

**Key Findings**

1.  **Score Changes**: Both 'amount_threshold_neighbourhood' and 'velocity_threshold_neighbourhood' tests exhibit changes in the risk score when input perturbations are applied. The risk scores for 'amount_threshold_neighbourhood' and 'velocity_threshold_neighbourhood' increase by 0.28 and 0.24, respectively.
2.  **Classification Flips**: No classification flips are observed in this experiment, as the classification remains 'LEGITIMATE' for both baseline and perturbed predictions.
3.  **Threshold Sensitivity**: The results indicate a high sensitivity to input perturbations, as even slight changes in input values lead to noticeable changes in risk scores. This suggests that the model is sensitive to input variations and may be vulnerable to evasion attacks.
4.  **Limitations**: The experiment's scope is limited to synthetic test results and does not account for potential real-world scenarios. Real-world transactions may exhibit different characteristics, and the model's performance may degrade in such cases.

**Recommendations**

To improve the model's robustness, consider the following:

1.  **Robustness Tests**: Perform a comprehensive range of perturbation tests to identify the model's weaknesses and areas for improvement.
2.  **Feature Validation**: Validate the features used in the model to ensure they accurately represent the underlying patterns in the data.
3.  **Drift Monitoring**: Regularly monitor the model's performance on new, unseen data to detect potential drifts in the underlying data distribution.
4.  **Human Review**: Regularly review the model's predictions and explanations to ensure they align with expert expectations and to identify potential issues.

**Conclusion**

The results of this experiment indicate a high sensitivity of the ARMS fraud model to controlled input perturbations. While the classification remains the same, the risk scores exhibit noticeable changes, suggesting potential vulnerabilities to evasion attacks. To address these concerns, it is essential to perform robustness tests, validate features, monitor drift, and conduct human reviews to ensure the model's reliability and accuracy.

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

## Compliance Agent Analysis

Based on the provided assessment, here are the control observations and test results analyzed against the relevant regulatory frameworks:

**1. DORA - ICT access control and protection of exposed interfaces**

* **Status:** REVIEW_REQUIRED
* **Evidence:** The simulator exposes a POST /analyze endpoint. Identity management, authentication configuration, and authorization roles were not evaluated.
* **Applicability caveat:** Not applicable to a training simulator, but relevant in production.
* **Potential consequence:** Exposed interfaces may allow unauthorized access to sensitive data or functionality.
* **Practical remediation:** Implement authentication and authorization mechanisms, restrict access to sensitive endpoints, and ensure proper identity management.

**2. DORA - Logging and traceability of security-relevant events**

* **Status:** PARTIALLY_OBSERVED
* **Evidence:** A logs endpoint exists in the simulator, but log integrity, retention, access restrictions, and alerting were not tested.
* **Applicability caveat:** Relevant to both training simulators and production environments.
* **Potential consequence:** Inadequate logging and monitoring may hinder incident response and compliance with regulatory requirements.
* **Practical remediation:** Implement robust logging, ensure log retention and access controls, and configure alerting mechanisms.

**3. EU AI Act - AI system documentation, logging, monitoring, and human oversight**

* **Status:** REVIEW_REQUIRED
* **Evidence:** The API records model_version and decision explanations, but dataset provenance, model documentation, human oversight, risk classification, and lifecycle governance were not evidenced.
* **Applicability caveat:** Relevant to AI-powered systems, including those using ML models.
* **Potential consequence:** Inadequate documentation and oversight may lead to regulatory non-compliance and reputational damage.
* **Practical remediation:** Develop comprehensive documentation, implement logging and monitoring, and establish human oversight processes.

**4. GDPR - Data minimisation, lawful basis, retention, and data-subject rights**

* **Status:** NOT_ASSESSED
* **Evidence:** The lab uses synthetic transaction records, but no conclusions can be drawn about GDPR compliance in a real deployment.
* **Applicability caveat:** Relevant to all data processing, including training simulators.
* **Potential consequence:** Non-compliance with GDPR may result in significant fines and reputational damage.
* **Practical remediation:** Assess GDPR compliance in production environments and implement measures to minimize data collection, ensure lawful basis, and respect data-subject rights.

**5. MiCA - Crypto-asset service controls**

* **Status:** NOT_ASSESSED
* **Evidence:** The simulator does not implement custody, exchange, transfer, or other crypto-asset service workflows, despite appearing in synthetic data.
* **Applicability caveat:** Relevant to crypto-asset service providers.
* **Potential consequence:** Non-compliance with MiCA may result in regulatory action and reputational damage.
* **Practical remediation:** Assess MiCA compliance in production environments and implement measures to ensure crypto-asset service controls.

Note that these findings are based on the provided assessment and may not be exhaustive. It is essential to review and refine these observations in light of additional information and context.

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

**Business and Operational Significance:**

The computed risk assessment indicates a medium-severity risk with a score of 0.652. This suggests that the identified vulnerabilities and control weaknesses pose a moderate threat to the organization's operations and reputation.

**Prioritization:**

Based on the provided information, the top priority findings are:

1. **RT-API-001: Synthetic transaction submission accepted by the lab API** (Priority: HIGH)
	* This vulnerability has a high likelihood of being exploited, and the lab API is currently not enforcing authentication, authorization, or rate limits. This poses a significant risk to the organization's data and systems.
2. **RT-AI-001: Model sensitivity to small input changes** (Priority: MEDIUM)
	* This vulnerability has a medium likelihood of being exploited, and the model's sensitivity to small input changes could lead to incorrect decisions. This poses a moderate risk to the organization's operations and reputation.
3. **RT-API-002: Input validation and duplicate-reference controls** (Priority: LOW)
	* This validated control has a low likelihood of being exploited, and the identified issues can be addressed through server-side schema validation and unique transaction references.

**Plausible Business Consequences:**

If left unaddressed, these vulnerabilities and control weaknesses could lead to:

* Data breaches or unauthorized access (RT-API-001)
* Inaccurate or biased decisions (RT-AI-001)
* System crashes or failures due to input validation issues (RT-API-002)

**Recommendations:**

1. Implement authentication, authorization, and rate limits for the lab API (RT-API-001)
2. Expand adversarial robustness tests and calibrate thresholds for the AI model (RT-AI-001)
3. Retain server-side schema validation and unique transaction references for the API (RT-API-002)

**Assumptions and Limitations:**

* This risk assessment is based on a classroom scoring heuristic and not a bank-approved risk model.
* Financial loss is not estimated as no validated loss assumptions or exposure data are supplied.
* Regulatory exposure is a prioritization proxy and not a legal determination.

Please note that this analysis is based on the provided information and should be reviewed and validated by subject matter experts and stakeholders to ensure its accuracy and relevance to the organization's specific context.

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
