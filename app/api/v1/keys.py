import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.search_key import SearchKey

router = APIRouter()

class KeyCreate(BaseModel):
    name: str
    keywords: str | None = None
    region: str | None = None
    law: str | None = None
    price_from: float | None = None
    price_to: float | None = None

class KeyOut(BaseModel):
    id: str
    name: str
    keywords: str | None = None
    region: str | None = None
    law: str | None = None
    price_from: float | None = None
    price_to: float | None = None
    count: int = 0

@router.get("", response_model=list[KeyOut])
async def list_keys(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SearchKey).order_by(SearchKey.created_at.desc()))
    keys = result.scalars().all()
    return [{"id": str(k.id), "name": k.name, "keywords": k.keywords, "region": k.region, "law": k.law, "price_from": k.price_from, "price_to": k.price_to, "count": 0} for k in keys]

@router.post("", response_model=KeyOut)
async def create_key(body: KeyCreate, db: AsyncSession = Depends(get_db)):
    key = SearchKey(name=body.name, keywords=body.keywords, region=body.region, law=body.law, price_from=body.price_from, price_to=body.price_to)
    db.add(key); await db.commit(); await db.refresh(key)
    return {"id": str(key.id), "name": key.name, "keywords": key.keywords, "region": key.region, "law": key.law, "price_from": key.price_from, "price_to": key.price_to, "count": 0}

@router.put("/{key_id}", response_model=KeyOut)
async def update_key(key_id: str, body: KeyCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SearchKey).where(SearchKey.id == key_id))
    key = result.scalar_one_or_none()
    if not key: raise HTTPException(status_code=404, detail="Key not found")
    key.name = body.name; key.keywords = body.keywords; key.region = body.region; key.law = body.law
    key.price_from = body.price_from; key.price_to = body.price_to
    await db.commit(); await db.refresh(key)
    return {"id": str(key.id), "name": key.name, "keywords": key.keywords, "region": key.region, "law": key.law, "price_from": key.price_from, "price_to": key.price_to, "count": 0}

@router.delete("/{key_id}")
async def delete_key(key_id: str, db: AsyncSession = Depends(get_db)):
    await db.execute(delete(SearchKey).where(SearchKey.id == key_id))
    await db.commit()
    return {"ok": True}