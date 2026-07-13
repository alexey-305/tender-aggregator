import asyncio
from app.db.session import async_session_maker
from app.models.tender import Tender
from sqlalchemy import select

async def main():
    async with async_session_maker() as s:
        r = await s.execute(select(Tender).where(Tender.external_id == "0348100069026000024"))
        t = r.scalar_one_or_none()
        if t and t.raw_data:
            rd = t.raw_data
            
            def dict_to_xml(d, parent):
                from lxml import etree
                if isinstance(d, dict):
                    for k, v in d.items():
                        child = etree.SubElement(parent, k)
                        dict_to_xml(v, child)
                elif isinstance(d, list):
                    for item in d:
                        dict_to_xml(item, parent)
                elif d is not None:
                    parent.text = str(d)
            
            from lxml import etree
            root = etree.Element("root")
            dict_to_xml(rd, root)
            
            found = root.xpath(".//*[local-name()='summarizingDate']")
            print("Found summarizingDate:", len(found))
            if found:
                print("Text:", found[0].text)

asyncio.run(main())