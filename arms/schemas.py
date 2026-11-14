"""Pydantic request and response schemas."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction_ref: str = Field(min_length=3, max_length=40)
    amount: float = Field(gt=0, le=10_000_000)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    country_code: str = Field(default="FR", min_length=2, max_length=2)
    merchant_category: str = Field(default="retail", min_length=2, max_length=40)
    channel: str = Field(default="online", min_length=2, max_length=20)
    account_age_days: int = Field(default=365, ge=0, le=20_000)
    transactions_last_hour: int = Field(default=1, ge=0, le=10_000)
    is_cross_border: bool = False


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_ref: str
    amount: float
    currency: str
    country_code: str
    merchant_category: str
    channel: str
    account_age_days: int
    transactions_last_hour: int
    is_cross_border: bool
    status: str
    risk_score: float | None
    classification: str | None
    anomaly_score: float | None
    model_version: str | None
    created_at: datetime


class AnalysisResponse(BaseModel):
    transaction: TransactionResponse
    explanation: list[str]
    decision: str


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    entity_type: str
    entity_id: str
    details: str
    created_at: datetime
