"""Reproducible robustness evaluation using synthetic transactions only.

Metrics describe this simulator and its synthetic labels; they are not estimates
of production fraud performance or regulatory compliance.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from types import SimpleNamespace
from typing import Any

import numpy as np

from arms.fraud_detection import fraud_engine


DECISION_THRESHOLD = 0.60  # mirrors the SUSPICIOUS threshold in arms/fraud_detection.py


@dataclass
class EvaluationCase:
    case_id: str
    expected: str
    actual: str
    risk_score: float
    passed: bool


def _transaction(**overrides: Any) -> SimpleNamespace:
    values = {
        "amount": 120.0,
        "account_age_days": 800,
        "transactions_last_hour": 1,
        "is_cross_border": False,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def run_robustness_evaluation() -> dict:
    """Evaluate a fixed synthetic cohort and threshold-adjacent perturbations."""
    # These labels are scenario definitions, not observed fraud ground truth.
    cohort = [
        ("benign_low_value", "LEGITIMATE", _transaction(amount=35, account_age_days=900, transactions_last_hour=1)),
        ("benign_cross_border", "LEGITIMATE", _transaction(amount=180, is_cross_border=True)),
        ("high_amount", "SUSPICIOUS", _transaction(amount=6500)),
        ("high_velocity", "SUSPICIOUS", _transaction(transactions_last_hour=7)),
        ("new_account_cross_border", "SUSPICIOUS", _transaction(account_age_days=4, is_cross_border=True)),
        ("combined_signals", "SUSPICIOUS", _transaction(amount=7200, transactions_last_hour=8, account_age_days=5, is_cross_border=True)),
    ]
    cases: list[EvaluationCase] = []
    details: dict[str, dict] = {}
    for case_id, expected, tx in cohort:
        result = fraud_engine.analyze(tx)
        cases.append(EvaluationCase(case_id, expected, result.classification, result.risk_score, result.classification == expected))
        rules = [e for e in result.explanation if not e.startswith("Isolation Forest") and not e.startswith("No configured")]
        details[case_id] = {
            "triggered_rules": rules,
            "anomaly_score": result.anomaly_score,
            "decision_threshold": DECISION_THRESHOLD,
            "gap_to_threshold": round(max(DECISION_THRESHOLD - result.risk_score, 0), 4),
            "cause": (
                f"{len(rules)} rule(s) triggered; combined score {result.risk_score} < threshold {DECISION_THRESHOLD} "
                "(rule score is weighted 0.80 and the anomaly signal adds at most 0.20)."
            ) if expected == "SUSPICIOUS" and result.classification != "SUSPICIOUS" else None,
        }

    # Small perturbations around configured rule boundaries: amount 5,000 and
    # velocity 5. We report flips rather than claiming all flips are defects.
    perturbations = [
        ("amount_threshold", _transaction(amount=4999), _transaction(amount=5001)),
        ("velocity_threshold", _transaction(transactions_last_hour=4), _transaction(transactions_last_hour=5)),
        ("account_age_threshold", _transaction(account_age_days=30), _transaction(account_age_days=29)),
    ]
    flips = []
    for name, baseline, changed in perturbations:
        before = fraud_engine.analyze(baseline)
        after = fraud_engine.analyze(changed)
        flips.append({
            "test": name,
            "baseline_classification": before.classification,
            "perturbed_classification": after.classification,
            "classification_changed": before.classification != after.classification,
            "baseline_risk_score": before.risk_score,
            "perturbed_risk_score": after.risk_score,
            "risk_delta": round(after.risk_score - before.risk_score, 4),
            "interpretation": "Expected threshold sensitivity; review business calibration." if before.classification != after.classification else "No classification flip observed.",
        })

    passed = sum(case.passed for case in cases)
    confusion = {key: 0 for key in ("tp", "tn", "fp", "fn")}
    for case in cases:
        if case.expected == "SUSPICIOUS" and case.actual == "SUSPICIOUS": confusion["tp"] += 1
        elif case.expected == "LEGITIMATE" and case.actual == "LEGITIMATE": confusion["tn"] += 1
        elif case.expected == "LEGITIMATE": confusion["fp"] += 1
        else: confusion["fn"] += 1
    precision = confusion["tp"] / max(confusion["tp"] + confusion["fp"], 1)
    recall = confusion["tp"] / max(confusion["tp"] + confusion["fn"], 1)
    return {
        "evaluation_scope": "Fixed synthetic scenario cohort; expected labels are authored test expectations, not real-world ground truth.",
        "model_version": "arms-baseline-1.0",
        "cohort_size": len(cases),
        "passed_cases": passed,
        "scenario_pass_rate": round(passed / len(cases), 4),
        "confusion_counts": confusion,
        "synthetic_precision": round(precision, 4),
        "synthetic_recall": round(recall, 4),
        "cases": [{**asdict(case), **details[case.case_id]} for case in cases],
        "threshold_perturbations": flips,
        "limitations": [
            "Synthetic scenario labels are not verified fraud labels.",
            "Small cohort; metrics are demonstrative and not statistically representative.",
            "No model retraining, data poisoning, or production data access is performed.",
        ],
    }
