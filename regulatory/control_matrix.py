"""Evidence-oriented control mapping; not legal advice or a compliance verdict."""

CONTROL_MATRIX = [
    {"framework": "DORA", "reference": "Article 9", "theme": "Protection and prevention", "test": "API access control and least privilege", "evidence_key": "conventional_attack", "status_rule": "REVIEW_REQUIRED", "note": "The simulator exposes analysis and read endpoints; authentication/authorization controls are not implemented in this lab."},
    {"framework": "DORA", "reference": "Article 10", "theme": "Detection", "test": "Monitoring, anomaly detection and alert handling", "evidence_key": "robustness", "status_rule": "PARTIAL_EVIDENCE", "note": "Synthetic detection scenarios are evaluated; operational monitoring and alert SLAs are outside scope."},
    {"framework": "DORA", "reference": "Article 17", "theme": "ICT-related incident management", "test": "Incident classification, escalation and evidence retention", "evidence_key": "audit_logs", "status_rule": "NOT_VERIFIED", "note": "Audit events exist; retention, tamper resistance and escalation workflows are not tested."},
    {"framework": "GDPR", "reference": "Articles 5 and 25", "theme": "Data minimisation and privacy by design", "test": "Purpose limitation, minimisation and privacy controls", "evidence_key": "data_scope", "status_rule": "NOT_ASSESSED", "note": "Only synthetic data is used; no personal-data processing assessment is performed."},
    {"framework": "GDPR", "reference": "Article 32", "theme": "Security of processing", "test": "Confidentiality, integrity, availability and resilience", "evidence_key": "conventional_attack", "status_rule": "PARTIAL_EVIDENCE", "note": "Input validation and duplicate handling are tested; encryption, access management and resilience are not assessed."},
    {"framework": "EU AI Act", "reference": "Articles 9, 10 and 15", "theme": "Risk, data governance and robustness", "test": "Model risk, data quality, robustness and cybersecurity", "evidence_key": "robustness", "status_rule": "PARTIAL_EVIDENCE", "note": "Synthetic robustness tests are provided; legal high-risk classification and full lifecycle controls require separate assessment."},
    {"framework": "EU AI Act", "reference": "Articles 12 and 14", "theme": "Record-keeping and human oversight", "test": "Traceability, logging and human intervention", "evidence_key": "audit_logs", "status_rule": "PARTIAL_EVIDENCE", "note": "Model version and explanations are logged; human oversight workflow is not implemented."},
    {"framework": "MiCA", "reference": "Conditional applicability", "theme": "Crypto-asset services", "test": "Determine whether crypto-asset services are in scope", "evidence_key": "crypto_scope", "status_rule": "NOT_ASSESSED", "note": "A merchant-category string alone does not establish a crypto-asset service or MiCA applicability."},
]


def build_control_matrix() -> dict:
    return {
        "disclaimer": "Indicative evidence mapping for a classroom simulator. It is not a legal opinion, formal gap assessment, or compliance certification.",
        "controls": CONTROL_MATRIX,
        "status_legend": {
            "REVIEW_REQUIRED": "A control area is exposed by the simulator and needs direct review.",
            "PARTIAL_EVIDENCE": "Some limited test evidence exists; the control is not fully validated.",
            "NOT_VERIFIED": "The control has not been tested.",
            "NOT_ASSESSED": "Applicability or evidence has not been assessed.",
        },
    }
