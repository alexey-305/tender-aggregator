import asyncio
from app.db.session import async_session_maker
from app.models.tender import Tender
from sqlalchemy import select
from lxml import etree

async def main():
    async with async_session_maker() as s:
        r = await s.execute(select(Tender).where(Tender.external_id == "0348100069026000024"))
        t = r.scalar_one_or_none()
        if t and t.raw_data:
            rd = t.raw_data
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
            xml_bytes = etree.tostring(root)
            
            # Вызовем _find_text напрямую
            from app.services.parsers.eis.xml_mapper import _find_text
            result = _find_text(root, "endDT")
            print("_find_text result:", result)
            
            result2 = _find_text(root, "collectingEndDate", "endDate", "submissionCloseDateTime", "endDT")
            print("_find_text multi result:", result2)

asyncio.run(main())