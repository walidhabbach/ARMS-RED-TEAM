import os
from pathlib import Path

# Remove the previous test database before importing the API/database modules.
Path("test_arms.db").unlink(missing_ok=True)
os.environ["DATABASE_URL"] = "sqlite:///./test_arms.db"

from fastapi.testclient import TestClient
from arms.api import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_analyze_high_risk_transaction():
    with TestClient(app) as client:
        payload = {
            "transaction_ref": "TEST-HIGH-001",
            "amount": 12500,
            "currency": "EUR",
            "country_code": "FR",
            "merchant_category": "crypto_exchange",
            "channel": "online",
            "account_age_days": 5,
            "transactions_last_hour": 9,
            "is_cross_border": True,
        }
        response = client.post("/analyze", json=payload)
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["decision"] == "SUSPICIOUS"
        assert body["transaction"]["risk_score"] >= 0.60
        assert body["transaction"]["model_version"] == "arms-baseline-1.0"


def test_analyze_normal_transaction():
    with TestClient(app) as client:
        payload = {
            "transaction_ref": "TEST-NORMAL-001",
            "amount": 42.50,
            "currency": "EUR",
            "country_code": "FR",
            "merchant_category": "groceries",
            "channel": "card",
            "account_age_days": 900,
            "transactions_last_hour": 1,
            "is_cross_border": False,
        }
        response = client.post("/analyze", json=payload)
        assert response.status_code == 200, response.text
        assert response.json()["decision"] == "LEGITIMATE"


def test_duplicate_reference_is_rejected():
    with TestClient(app) as client:
        payload = {
            "transaction_ref": "TEST-DUPLICATE-001",
            "amount": 20,
            "currency": "EUR",
            "country_code": "FR",
            "merchant_category": "retail",
            "channel": "card",
            "account_age_days": 500,
            "transactions_last_hour": 1,
            "is_cross_border": False,
        }
        first = client.post("/transactions", json=payload)
        second = client.post("/transactions", json=payload)
        assert first.status_code == 201
        assert second.status_code == 409
