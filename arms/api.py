"""ARMS simulator REST API. Use only synthetic data in this training environment."""
import json
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from arms.database import AuditLog, Transaction, get_db, init_db
from arms.fraud_detection import fraud_engine
from arms.schemas import (
    AnalysisResponse,
    AuditLogResponse,
    TransactionCreate,
    TransactionResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="ARMS – Agentic Risk Monitoring System (Simulation)",
    description="Synthetic banking transaction and fraud-monitoring API for a controlled Red Team lab.",
    version="1.0.0",
    lifespan=lifespan,
)


def write_audit(db: Session, event_type: str, entity_type: str, entity_id: str, details: dict) -> None:
    db.add(
        AuditLog(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=str(entity_id),
            details=json.dumps(details, ensure_ascii=False),
        )
    )


@app.get("/health")
def health():
    return {"status": "ok", "service": "ARMS-simulator", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/transactions", response_model=TransactionResponse, status_code=201)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(Transaction).where(Transaction.transaction_ref == payload.transaction_ref))
    if existing:
        raise HTTPException(status_code=409, detail="transaction_ref already exists")

    transaction = Transaction(**payload.model_dump(), status="PENDING")
    db.add(transaction)
    db.flush()
    write_audit(
        db,
        "TRANSACTION_CREATED",
        "transaction",
        transaction.id,
        {"transaction_ref": transaction.transaction_ref, "status": "PENDING"},
    )
    db.commit()
    db.refresh(transaction)
    return transaction


@app.post("/analyze", response_model=AnalysisResponse)
def analyze_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    """Create and analyze a transaction in one request."""
    existing = db.scalar(select(Transaction).where(Transaction.transaction_ref == payload.transaction_ref))
    if existing:
        raise HTTPException(status_code=409, detail="transaction_ref already exists")

    transaction = Transaction(**payload.model_dump(), status="PENDING")
    db.add(transaction)
    db.flush()

    result = fraud_engine.analyze(transaction)
    transaction.risk_score = result.risk_score
    transaction.classification = result.classification
    transaction.anomaly_score = result.anomaly_score
    transaction.model_version = result.model_version
    transaction.status = "ANALYZED"

    write_audit(
        db,
        "TRANSACTION_ANALYZED",
        "transaction",
        transaction.id,
        {
            "transaction_ref": transaction.transaction_ref,
            "classification": result.classification,
            "risk_score": result.risk_score,
            "model_version": result.model_version,
            "explanation": result.explanation,
        },
    )
    db.commit()
    db.refresh(transaction)
    return AnalysisResponse(
        transaction=transaction,
        explanation=result.explanation,
        decision=result.classification,
    )


@app.get("/transactions", response_model=list[TransactionResponse])
def list_transactions(limit: int = Query(default=50, ge=1, le=500), db: Session = Depends(get_db)):
    return list(db.scalars(select(Transaction).order_by(desc(Transaction.id)).limit(limit)).all())


@app.get("/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.get("/alerts", response_model=list[TransactionResponse])
def list_alerts(limit: int = Query(default=50, ge=1, le=500), db: Session = Depends(get_db)):
    query = (
        select(Transaction)
        .where(Transaction.classification == "SUSPICIOUS")
        .order_by(desc(Transaction.risk_score))
        .limit(limit)
    )
    return list(db.scalars(query).all())


@app.get("/logs", response_model=list[AuditLogResponse])
def list_logs(limit: int = Query(default=100, ge=1, le=1000), db: Session = Depends(get_db)):
    return list(db.scalars(select(AuditLog).order_by(desc(AuditLog.id)).limit(limit)).all())
