from fastapi import FastAPI

from database import engine, Base
from models.tender import Tender
from api.tenders import router as tender_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Tender Aggregator API",
    version="0.3.0"
)


app.include_router(
    tender_router
)


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Tender Aggregator"
    }