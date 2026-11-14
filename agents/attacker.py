"""Conventional attack simulation using synthetic data and local API only."""
import os
import uuid
import httpx
from agents.runtime import build_agent, run_text

BASE_URL = os.getenv("ARMS_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def run_conventional_simulation() -> dict:
    """Test unauthenticated synthetic submission, validation, and duplicate protection."""
    timeout = float(os.getenv("ARMS_HTTP_TIMEOUT", "8"))
    ref = f"RT-CYBER-{uuid.uuid4().hex[:10].upper()}"
    payload = {
        "transaction_ref": ref,
        "amount": 7600.0,
        "currency": "EUR",
        "country_code": "FR",
        "merchant_category": "retail",
        "channel": "online",
        "account_age_days": 12,
        "transactions_last_hour": 6,
        "is_cross_border": True,
    }
    invalid_payload = {**payload, "transaction_ref": f"{ref}-INVALID", "amount": -10}

    with httpx.Client(timeout=timeout) as client:
        # This is a controlled synthetic request to the local lab API.
        submit = client.post(f"{BASE_URL}/analyze", json=payload)
        validation = client.post(f"{BASE_URL}/analyze", json=invalid_payload)
        duplicate = client.post(f"{BASE_URL}/transactions", json=payload)

    result = {
        "scenario": "synthetic_transaction_injection_and_validation_test",
        "target": BASE_URL,
        "tests": [
            {
                "name": "synthetic_transaction_submission",
                "http_status": submit.status_code,
                "accepted": submit.status_code == 200,
                "authorization_header_sent": False,
                "response": submit.json() if submit.headers.get("content-type", "").startswith("application/json") else submit.text[:300],
                "interpretation": "A test transaction was accepted without an Authorization header; this is a lab observation, not proof of a production breach."
            },
            {
                "name": "negative_amount_validation",
                "http_status": validation.status_code,
                "rejected_as_expected": validation.status_code == 422,
            },
            {
                "name": "duplicate_reference_protection",
                "http_status": duplicate.status_code,
                "rejected_as_expected": duplicate.status_code == 409,
            },
        ],
        "scope": "Local ARMS simulator and synthetic records only",
    }
    return result


_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent(
            name="Attacker Agent",
            role="Evaluate conventional API and transaction-handling weaknesses in the lab",
            instructions=(
                "You are a controlled defensive security-testing analyst. Interpret only the supplied "
                "HTTP test evidence. Identify whether each control behaved as expected. Do not provide "
                "exploit instructions for real systems. Distinguish a successful synthetic test request "
                "from a confirmed security breach. Return findings, evidence, severity rationale, and fixes."
            ),
        )
    return _agent

def run_attacker() -> dict:
    evidence = run_conventional_simulation()
    analysis = run_text(get_agent(), f"Assess this controlled conventional security test:\n{evidence}")
    return {"evidence": evidence, "analysis": analysis}
