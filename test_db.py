import asyncio
import asyncpg

async def test():
    try:
        conn = await asyncpg.connect('postgresql://tender:tender@host.docker.internal:5432/tender_aggregator')
        count = await conn.fetchval('SELECT COUNT(*) FROM tenders')
        print('OK, count:', count)
        await conn.close()
    except Exception as e:
        print('Error:', e)

asyncio.run(test())