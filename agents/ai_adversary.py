"""AI adversary agent: controlled feature-perturbation tests on synthetic records."""
import os
import uuid
import httpx
from agents.runtime import build_agent, run_text

BASE_URL = os.getenv("ARMS_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def run_perturbation_tests() -> dict:
    """Compare baseline and slightly modified synthetic inputs through ARMS /analyze."""
    timeout = float(os.getenv("ARMS_HTTP_TIMEOUT", "8"))
    cases = [
        {
            "name": "amount_threshold_neighbourhood",
            "baseline": {"amount": 4900.0, "transactions_last_hour": 1, "account_age_days": 240, "is_cross_border": False},
            "perturbed": {"amount": 5100.0, "transactions_last_hour": 1, "account_age_days": 240, "is_cross_border": False},
        },
        {
            "name": "velocity_threshold_neighbourhood",
            "baseline": {"amount": 850.0, "transactions_last_hour": 4, "account_age_days": 240, "is_cross_border": False},
            "perturbed": {"amount": 850.0, "transactions_last_hour": 5, "account_age_days": 240, "is_cross_border": False},
        },
    ]
    results = []
    with httpx.Client(timeout=timeout) as client:
        for case in cases:
            pair = []
            for label, features in (("baseline", case["baseline"]), ("perturbed", case["perturbed"])):
                payload = {
                    "transaction_ref": f"RT-AI-{uuid.uuid4().hex[:10].upper()}",
                    "currency": "EUR",
                    "country_code": "FR",
                    "merchant_category": "retail",
                    "channel": "online",
                    "is_cross_border": features["is_cross_border"],
                    "amount": features["amount"],
                    "transactions_last_hour": features["transactions_last_hour"],
                    "account_age_days": features["account_age_days"],
                }
                response = client.post(f"{BASE_URL}/analyze", json=payload)
                response.raise_for_status()
                body = response.json()
                transaction = body["transaction"]
                pair.append({
                    "variant": label,
                    "risk_score": transaction["risk_score"],
                    "classification": transaction["classification"],
                    "anomaly_score": transaction["anomaly_score"],
                    "explanation": body.get("explanation", []),
                })
            results.append({
                "test": case["name"],
                "baseline": pair[0],
                "perturbed": pair[1],
                "classification_changed": pair[0]["classification"] != pair[1]["classification"],
                "risk_score_delta": round(pair[1]["risk_score"] - pair[0]["risk_score"], 4),
            })
    return {
        "scenario": "synthetic_input_perturbation",
        "target": BASE_URL,
        "tests": results,
        "scope": "Synthetic transaction feature changes; no training data or production model was modified.",
        "interpretation_note": "A changed score is a sensitivity signal, not by itself proof of exploitable model evasion.",
    }


_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent(
            name="AI Adversary Agent",
            role="Evaluate sensitivity of the ARMS fraud model to controlled input perturbations",
            instructions=(
                "You are an adversarial-ML evaluator working only with synthetic test results. Compare "
                "baseline and perturbed predictions. Identify score changes, classification flips, "
                "threshold sensitivity, and limitations. Do not claim data poisoning: this experiment "
                "does not modify training data. Recommend robustness tests, feature validation, drift "
                "monitoring, and human review."
            ),
        )
    return _agent

def run_ai_adversary() -> dict:
    evidence = run_perturbation_tests()
    analysis = run_text(get_agent(), f"Analyze these controlled AI input-perturbation results:\n{evidence}")
    return {"evidence": evidence, "analysis": analysis}
