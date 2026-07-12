import asyncio
from app.db.session import async_session_maker
from app.models.tender import Tender
from sqlalchemy import select
from lxml import etree
import json

async def main():
    async with async_session_maker() as s:
        r = await s.execute(select(Tender).where(Tender.external_id == "0348100069026000024"))
        t = r.scalar_one_or_none()
        if t and t.raw_data:
            # Convert raw_data back to XML
            rd = t.raw_data
            # Reconstruct XML from raw_data dict
            def dict_to_xml(d, parent):
                if isinstance(d, dict):
                    for k, v in d.items():
                        child = etree.SubElement(parent, k)
                        dict_to_xml(v, child)
                elif isinstance(d, list):
                    for item in d:
                        dict_to_xml(item, parent)
                elif d is not None:
                    parent.text = str(d)
            
            root = etree.Element("root")
            dict_to_xml(rd, root)
            
            # Try to find endDT
            found = root.xpath(".//*[local-name()='endDT']")
            print("Found endDT:", len(found))
            if found:
                print("Text:", found[0].text)
            
            # Try to find collectingInfo
            found2 = root.xpath(".//*[local-name()='collectingInfo']")
            print("Found collectingInfo:", len(found2))

asyncio.run(main())