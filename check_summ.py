import asyncio
from app.db.session import async_session_maker
from app.models.tender import Tender
from sqlalchemy import select, func

async def main():
    async with async_session_maker() as s:
        total = await s.scalar(select(func.count()).select_from(Tender))
        with_sd = await s.scalar(select(func.count()).select_from(Tender).where(Tender.submission_deadline.isnot(None)))
        with_summ = await s.scalar(select(func.count()).select_from(Tender).where(Tender.summarizing_date.isnot(None)))
        print(f"Total: {total}, With deadline: {with_sd}, With summarizing: {with_summ}")

asyncio.run(main())