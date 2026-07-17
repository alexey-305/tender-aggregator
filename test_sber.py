import asyncio
from app.services.collectors.sberbank_collector import SberbankCollector

async def main():
    c = SberbankCollector()
    r = await c.collect()
    print(f"Saved: {r.saved}, Errors: {r.errors}")

asyncio.run(main())