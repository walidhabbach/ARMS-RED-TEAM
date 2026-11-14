"""Insert a reproducible set of synthetic, low-risk baseline transactions."""
from arms.database import SessionLocal, Transaction, init_db


def seed() -> None:
    init_db()
    db = SessionLocal()
    try:
        if db.query(Transaction).count() > 0:
            print("Database already contains transactions; seed skipped.")
            return
        for index in range(1, 21):
            db.add(
                Transaction(
                    transaction_ref=f"SEED-{index:03d}",
                    amount=round(15 + ((index * 37) % 420), 2),
                    currency="EUR",
                    country_code="FR",
                    merchant_category=["retail", "groceries", "transport", "restaurant"][index % 4],
                    channel="card" if index % 2 == 0 else "online",
                    account_age_days=180 + index * 12,
                    transactions_last_hour=index % 3,
                    is_cross_border=False,
                    status="PENDING",
                )
            )
        db.commit()
        print("Inserted 20 synthetic baseline transactions.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
