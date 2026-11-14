"""Reconnaissance agent: maps only the local ARMS simulator surface."""
import os
import httpx
from agents.runtime import build_agent, run_text
  
from pathlib import Path
 

def get_dependencies():
    requirements = Path("requirements.txt")

    if not requirements.exists():
        return []

    deps = []

    for line in requirements.read_text().splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        deps.append(line)

    # return ["FastAPI", "SQLite", "SQLAlchemy", "scikit-learn IsolationForest"]
    return deps

BASE_URL = os.getenv("ARMS_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

def collect_attack_surface() -> dict:
    """Read the local OpenAPI document and service inventory; performs GET only."""
    timeout = float(os.getenv("ARMS_HTTP_TIMEOUT", "8"))
    with httpx.Client(timeout=timeout) as client:
        health = client.get(f"{BASE_URL}/health")
        health.raise_for_status()
        openapi = client.get(f"{BASE_URL}/openapi.json")
        openapi.raise_for_status()
        transactions = client.get(f"{BASE_URL}/transactions", params={"limit": 5})
        transactions.raise_for_status()
        alerts = client.get(f"{BASE_URL}/alerts", params={"limit": 5})
        alerts.raise_for_status()
        logs = client.get(f"{BASE_URL}/logs", params={"limit": 5})
        logs.raise_for_status()

    paths = openapi.json().get("paths", {})
    endpoints = []
    for path, methods in paths.items():
        for method, details in methods.items():
            if method.lower() in {"get", "post", "put", "patch", "delete"}:
                endpoints.append({
                    "method": method.upper(),
                    "path": path,
                    "summary": details.get("summary", ""),
                    "operation_id": details.get("operationId", ""),
                })

    return {
        "target": "Local ARMS simulator",
        "base_url": BASE_URL,
        "health": health.json(),
        "endpoints": endpoints,
        "sample_transaction_count": len(transactions.json()),
        "sample_alert_count": len(alerts.json()),
        "sample_audit_event_count": len(logs.json()),
        "observed_dependencies": get_dependencies(),
        "limitations": [
            "Only the exposed local simulator API was inspected.",
            "No production infrastructure or external provider was contacted.",
            "The endpoint inventory does not prove that authentication is required or absent."
        ],
    }


_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent(
            name="Reconnaissance Agent",
            role="Map the authorized ARMS simulator attack surface",
            instructions=(
                "You are a defensive red-team reconnaissance analyst. Analyze only the supplied local "
                "ARMS simulator inventory. Identify exposed endpoints, data flows, dependencies, and "
                "testable attack surfaces. Distinguish observed facts from hypotheses. Never claim to "
                "have scanned external or production infrastructure. Return concise structured sections: "
                "observed_assets, data_flows, attack_surfaces, unknowns, recommended_safe_tests."
            ),
        )
    return _agent

def run_reconnaissance() -> dict:
    evidence = collect_attack_surface()
    analysis = run_text(get_agent(), f"Analyze this observed ARMS inventory:\n{evidence}")
    return {"evidence": evidence, "analysis": analysis}
