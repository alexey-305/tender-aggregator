import asyncio
from app.services.collectors.rts_collector import RTSCollector

async def main():
    c = RTSCollector()
    r = await c.collect()
    print(f"Saved: {r.saved}, Errors: {r.errors}")

asyncio.run(main())