"""Deterministic baseline fraud scoring plus an Isolation Forest anomaly signal.

The deterministic rules make demonstrations reproducible. The unsupervised model
adds a second signal; it is not treated as ground truth.
"""
from dataclasses import dataclass
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

MODEL_VERSION = "arms-baseline-1.0"
FEATURES = ["amount", "account_age_days", "transactions_last_hour", "is_cross_border"]


@dataclass
class DetectionResult:
    risk_score: float
    classification: str
    anomaly_score: float
    explanation: list[str]
    model_version: str = MODEL_VERSION


class FraudDetectionEngine:
    def __init__(self) -> None:
        self.scaler = StandardScaler()
        self.model = IsolationForest(
            n_estimators=150,
            contamination=0.05,
            random_state=42,
        )
        self._fit_baseline()

    def _fit_baseline(self) -> None:
        rng = np.random.default_rng(42)
        normal_data = np.column_stack(
            [
                rng.lognormal(mean=3.5, sigma=0.8, size=1000),
                rng.integers(90, 4000, size=1000),
                rng.integers(0, 4, size=1000),
                rng.binomial(1, 0.12, size=1000),
            ]
        )
        scaled = self.scaler.fit_transform(normal_data)
        self.model.fit(scaled)
        train_scores = self.model.score_samples(scaled)
        self.normal_score_low = float(np.percentile(train_scores, 1))
        self.normal_score_high = float(np.percentile(train_scores, 95))

    @staticmethod
    def _features(transaction) -> np.ndarray:
        return np.array(
            [[
                float(transaction.amount),
                float(transaction.account_age_days),
                float(transaction.transactions_last_hour),
                float(bool(transaction.is_cross_border)),
            ]]
        )

    def analyze(self, transaction) -> DetectionResult:
        risk = 0.0
        reasons: list[str] = []

        if transaction.amount >= 5_000:
            risk += 0.35
            reasons.append("High transaction amount (>= EUR 5,000).")
        if transaction.transactions_last_hour >= 5:
            risk += 0.30
            reasons.append("High transaction velocity (>= 5 transactions/hour).")
        if transaction.is_cross_border:
            risk += 0.15
            reasons.append("Cross-border transaction.")
        if transaction.account_age_days < 30:
            risk += 0.20
            reasons.append("Recently created account (< 30 days).")

        scaled = self.scaler.transform(self._features(transaction))
        raw_score = float(self.model.score_samples(scaled)[0])
        denominator = max(self.normal_score_high - self.normal_score_low, 1e-9)
        anomaly_score = float(
            np.clip((self.normal_score_high - raw_score) / denominator, 0.0, 1.0)
        )

        # The rule score has priority in this first-stage baseline. The model signal
        # contributes to the overall score but cannot silently override the rules.
        combined_score = float(np.clip(0.80 * risk + 0.20 * anomaly_score, 0.0, 1.0))
        classification = "SUSPICIOUS" if risk >= 0.60 or combined_score >= 0.60 else "LEGITIMATE"
        if not reasons:
            reasons.append("No configured high-risk rule was triggered.")
        reasons.append(f"Isolation Forest anomaly signal: {anomaly_score:.2f} (0–1).")

        return DetectionResult(
            risk_score=round(combined_score, 4),
            classification=classification,
            anomaly_score=round(anomaly_score, 4),
            explanation=reasons,
        )


fraud_engine = FraudDetectionEngine()
