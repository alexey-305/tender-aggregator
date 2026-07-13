import asyncio
from app.db.session import async_session_maker
from app.models.tender import Tender
from sqlalchemy import select

async def main():
    async with async_session_maker() as s:
        r = await s.execute(select(Tender).where(Tender.external_id == "0348100069026000024"))
        t = r.scalar_one_or_none()
        if t and t.raw_data:
            print("Keys:", list(t.raw_data.keys()))
            print("Has submission_deadline:", t.submission_deadline)

asyncio.run(main())