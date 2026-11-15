"""Impact and risk scoring: deterministic calculation plus LLM explanation."""
from agents.runtime import build_agent, run_text


def calculate_risk(attacker: dict, ai_adversary: dict, compliance: dict) -> dict:
    cyber_tests = attacker.get("evidence", {}).get("tests", [])
    injection = next((t for t in cyber_tests if t.get("name") == "synthetic_transaction_submission"), {})
    invalid = next((t for t in cyber_tests if t.get("name") == "negative_amount_validation"), {})
    duplicate = next((t for t in cyber_tests if t.get("name") == "duplicate_reference_protection"), {})
    ai_tests = ai_adversary.get("evidence", {}).get("tests", [])
    flips = sum(1 for test in ai_tests if test.get("classification_changed"))
    score_deltas = [abs(float(test.get("risk_score_delta", 0))) for test in ai_tests]
    max_delta = max(score_deltas, default=0.0)

    # Explicit scoring assumptions for this classroom simulator (0..1).
    business_impact = 0.70 if injection.get("accepted") else 0.35
    likelihood = 0.75 if injection.get("accepted") else 0.30
    regulatory_exposure = 0.65
    control_weakness = 0.70 if not invalid.get("rejected_as_expected") else 0.45
    if not duplicate.get("rejected_as_expected"):
        control_weakness = min(1.0, control_weakness + 0.15)
    if flips:
        control_weakness = min(1.0, control_weakness + 0.10)
        business_impact = min(1.0, business_impact + 0.10)

    score = round(
        0.35 * business_impact
        + 0.25 * likelihood
        + 0.20 * regulatory_exposure
        + 0.20 * control_weakness,
        3,
    )
    severity = "CRITICAL" if score >= 0.85 else "HIGH" if score >= 0.70 else "MEDIUM" if score >= 0.40 else "LOW"

    findings = [
        {
            "id": "RT-API-001",
            "title": "Synthetic transaction submission accepted by the lab API",
            "priority": "HIGH" if injection.get("accepted") else "INFO",
            "evidence": f"HTTP {injection.get('http_status', 'unknown')}",
            "remediation": "For a real deployment, enforce authentication, authorization, request signing where appropriate, rate limits and transaction provenance. The lab currently has no production identity layer.",
        },
        {
            "id": "RT-API-002",
            "title": "Input validation and duplicate-reference controls",
            "priority": "LOW" if invalid.get("rejected_as_expected") and duplicate.get("rejected_as_expected") else "HIGH",
            "evidence": f"Negative amount rejected={invalid.get('rejected_as_expected')}; duplicate rejected={duplicate.get('rejected_as_expected')}.",
            "remediation": "Retain server-side schema validation and unique transaction references; add regression tests for boundary values.",
        },
        {
            "id": "RT-AI-001",
            "title": "Model sensitivity to small input changes",
            "priority": "HIGH" if flips else "MEDIUM" if max_delta >= 0.10 else "LOW",
            "evidence": f"Classification flips={flips}; maximum absolute risk-score delta={max_delta:.3f}.",
            "remediation": "Expand adversarial robustness tests, calibrate thresholds, monitor drift and require human review for high-impact decisions.",
        },
    ]
    # RT-API-002 reports controls that work; flag it so it is not shown as a vulnerability.
    for f in findings:
        f["type"] = "validated_control" if f["id"] == "RT-API-002" and f["priority"] == "LOW" else "vulnerability"
    return {
        "score": score,
        "severity": severity,
        "scale": "0 to 1; higher means greater simulated risk",
        "formula": "0.35*business_impact + 0.25*likelihood + 0.20*regulatory_exposure + 0.20*control_weakness",
        "factors": {
            "business_impact": round(business_impact, 3),
            "likelihood": round(likelihood, 3),
            "regulatory_exposure": round(regulatory_exposure, 3),
            "control_weakness": round(control_weakness, 3),
        },
        "findings": findings,
        "limitations": [
            "This is a classroom scoring heuristic, not a bank-approved risk model.",
            "Financial loss is not estimated because no validated loss assumptions or exposure data are supplied.",
            "Regulatory exposure is a prioritisation proxy, not a legal determination.",
        ],
    }


_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent(
            name="Impact and Risk Scoring Agent",
            role="Explain the business and operational significance of validated findings",
            instructions=(
                "You are an operational risk analyst. Explain the supplied deterministic risk score, "
                "rank findings, describe plausible business consequences, and recommend remediation. "
                "Do not change the numeric score, invent monetary losses, or present a heuristic as a "
                "regulatory/legal assessment. State assumptions and limitations."
            ),
        )
    return _agent

def run_risk_scoring(attacker: dict, ai_adversary: dict, compliance: dict) -> dict:
    score = calculate_risk(attacker, ai_adversary, compliance)
    analysis = run_text(get_agent(), f"Explain and prioritize this computed risk assessment without changing its score:\n{score}")
    return {"evidence": score, "analysis": analysis}
