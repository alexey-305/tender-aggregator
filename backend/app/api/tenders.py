from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.tender import Tender
from schemas.tender import TenderCreate

from services.loaders import EISLoader


router = APIRouter(
    prefix="/tenders",
    tags=["Tenders"]
)


@router.get("/")
def get_tenders(
    db: Session = Depends(get_db)
):
    return db.query(Tender).all()



@router.post("/")
def create_tender(
    tender: TenderCreate,
    db: Session = Depends(get_db)
):

    new_tender = Tender(
        **tender.model_dump()
    )

    db.add(new_tender)
    db.commit()
    db.refresh(new_tender)

    return new_tender



@router.post("/load")
def load_tenders(
    db: Session = Depends(get_db)
):

    loader = EISLoader()

    items = loader.load()

    loaded = []


    for item in items:

        exists = (
            db.query(Tender)
            .filter(
                Tender.registry_number == item["registry_number"]
            )
            .first()
        )


        if exists:
            continue


        tender = Tender(**item)

        db.add(tender)

        loaded.append(item)


    db.commit()


    return {
        "source": "EIS",
        "loaded": len(loaded),
        "items": loaded
    }