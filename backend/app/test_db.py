from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg://tender:tender_password@127.0.0.1:5432/tender_db",
    echo=True
)

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print(result.fetchone())