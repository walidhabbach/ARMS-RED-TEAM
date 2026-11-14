"""Offline tests for Stage 2 logic; no LLM provider or running ARMS required."""
from agents.compliance_breaker import build_compliance_evidence
from agents.risk_scoring import calculate_risk


def sample_reports():
    recon = {"evidence": {"endpoints": [
        {"method": "POST", "path": "/analyze"},
        {"method": "GET", "path": "/logs"},
    ]}}
    attacker = {"evidence": {"tests": [
        {"name": "synthetic_transaction_submission", "http_status": 200, "accepted": True},
        {"name": "negative_amount_validation", "http_status": 422, "rejected_as_expected": True},
        {"name": "duplicate_reference_protection", "http_status": 409, "rejected_as_expected": True},
    ]}}
    ai = {"evidence": {"tests": [
        {"classification_changed": False, "risk_score_delta": 0.08},
        {"classification_changed": True, "risk_score_delta": 0.22},
    ]}}
    return recon, attacker, ai


def test_compliance_evidence_is_caveated():
    recon, attacker, ai = sample_reports()
    result = build_compliance_evidence(recon, attacker, ai)
    assert result["assessment_scope"].startswith("Training simulator")
    frameworks = {item["framework"] for item in result["controls"]}
    assert {"DORA", "MiCA", "EU AI Act", "GDPR"}.issubset(frameworks)
    mica = next(item for item in result["controls"] if item["framework"] == "MiCA")
    assert mica["status"] == "NOT_ASSESSED"


def test_risk_score_is_bounded_and_reproducible():
    recon, attacker, ai = sample_reports()
    compliance = build_compliance_evidence(recon, attacker, ai)
    result = calculate_risk(attacker, ai, compliance)
    assert 0 <= result["score"] <= 1
    assert result["severity"] in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    assert len(result["findings"]) == 3
    assert result["factors"]["control_weakness"] == 0.55
