"""Compliance agent with evidence-led control checks; not legal advice."""
from agents.runtime import build_agent, run_text


def build_compliance_evidence(recon: dict, attacker: dict, ai_adversary: dict) -> dict:
    endpoints = recon.get("evidence", {}).get("endpoints", [])
    endpoint_names = {f"{item['method']} {item['path']}" for item in endpoints}
    conventional = attacker.get("evidence", {}).get("tests", [])
    ai_tests = ai_adversary.get("evidence", {}).get("tests", [])

    return {
        "assessment_scope": "Training simulator only; findings are preliminary control observations, not legal conclusions.",
        "controls": [
            {
                "framework": "DORA",
                "control": "ICT access control and protection of exposed interfaces",
                "status": "REVIEW_REQUIRED" if "POST /analyze" in endpoint_names else "NOT_OBSERVED",
                "evidence": "The simulator exposes POST /analyze. The current test did not evaluate identity management, authentication configuration, or authorization roles.",
            },
            {
                "framework": "DORA",
                "control": "Logging and traceability of security-relevant events",
                "status": "PARTIALLY_OBSERVED" if "GET /logs" in endpoint_names else "NOT_OBSERVED",
                "evidence": "A logs endpoint exists in the simulator. Log integrity, retention, access restrictions, and alerting were not tested.",
            },
            {
                "framework": "EU AI Act",
                "control": "AI system documentation, logging, monitoring and human oversight where applicable",
                "status": "REVIEW_REQUIRED",
                "evidence": "The API records model_version and decision explanations. Dataset provenance, model documentation, human oversight, risk classification and lifecycle governance were not evidenced in this stage.",
            },
            {
                "framework": "GDPR",
                "control": "Data minimisation, lawful basis, retention and data-subject rights where personal data is processed",
                "status": "NOT_ASSESSED",
                "evidence": "The lab uses synthetic transaction records. No conclusion about GDPR compliance in a real deployment can be drawn.",
            },
            {
                "framework": "MiCA",
                "control": "Crypto-asset service controls where in-scope crypto-asset services are provided",
                "status": "NOT_ASSESSED",
                "evidence": "A crypto_exchange merchant category appears in synthetic data, but the simulator does not implement custody, exchange, transfer or other crypto-asset service workflows.",
            },
        ],
        "attack_test_summary": {
            "conventional_tests": conventional,
            "ai_perturbation_tests": ai_tests,
        },
        "not_tested": [
            "Real identity provider and role-based access control",
            "Third-party ICT provider contracts and exit plans",
            "Incident response and disaster recovery exercises",
            "Crypto-asset custody and key management",
            "Production personal data processing and retention",
        ],
    }


_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent(
            name="Compliance Breaker Agent",
            role="Identify evidence-backed regulatory control gaps",
            instructions=(
                "You are a regulatory technology control assessor. Review the supplied evidence against "
                "DORA, MiCA, the EU AI Act and GDPR only where applicable. Never invent an article-level "
                "breach or equate missing simulator functionality with a proven legal violation. Clearly "
                "label observations as observed, partially observed, review required, or not assessed. "
                "For each finding provide evidence, applicability caveat, potential consequence and a "
                "practical remediation."
            ),
        )
    return _agent

def run_compliance_breaker(recon: dict, attacker: dict, ai_adversary: dict) -> dict:
    evidence = build_compliance_evidence(recon, attacker, ai_adversary)
    analysis = run_text(get_agent(), f"Assess these control observations and test results:\n{evidence}")
    return {"evidence": evidence, "analysis": analysis}
