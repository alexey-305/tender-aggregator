import asyncio
from app.services.collectors.eis_223_collector import EIS223Collector
from app.services.collectors.base import CollectionConfig
from datetime import date

async def main():
    c = EIS223Collector()
    for d in [date(2026,7,1), date(2026,7,5), date(2026,7,8)]:
        print(f"\n=== Testing {d} ===")
        r = await c.collect(CollectionConfig(region="77", date_from=d))
        print(f"Saved: {r.saved}, Errors: {r.errors}")

asyncio.run(main())