import re

with open(r"C:\TenderAggregator\app\services\parsers\eis\client.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace request_archive_223 method
old_method = '''    def request_archive_223(self, org_region, exact_date, document_type): print("=== 223 CALLED ==="); """'''
new_method = '''    def request_archive_223(self, org_region: str, exact_date, document_type: str):
        """Запрос архива 223-ФЗ через getDocsLE."""
        import uuid as _uuid
        from datetime import datetime as _dt

        # Используем шаблон 44-ФЗ, но заменяем documentType44 на documentType223
        xml_body = SOAP_ENVELOPE_TEMPLATE.replace(
            "<documentType44>{document_type}</documentType44>",
            "<documentType223>{document_type}</documentType223>"
        ).format(
            namespace=settings.eis_ws_namespace,
            token=self.token,
            request_id=str(_uuid.uuid4()),
            created_at=_dt.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            org_region=org_region,
            subsystem_type="RI223",
            document_type=document_type,
            exact_date=exact_date.isoformat(),
        )
        print("=== 223 SOAP REQUEST ===")
        print(xml_body[:800])
        root = self._post(xml_body)
        print("=== 223 SOAP RESPONSE ===")
        print(etree.tostring(root, pretty_print=True).decode()[:1000])
        archive_url_elements = root.xpath("//*[local-name()='archiveUrl']")
        if not archive_url_elements or not archive_url_elements[0].text:
            fault = root.xpath("//*[local-name()='faultstring' or local-name()='errorMessage']")
            if fault:
                raise EISClientError(f"EIS error: {fault[0].text}")
            raise EISClientError("archiveUrl not found in 223-FZ response")
        from app.services.parsers.eis.client import ArchiveReference
        return ArchiveReference(
            url=archive_url_elements[0].text.strip(),
            document_type=document_type,
            region=org_region,
            requested_date=exact_date,
        )'''

content = content.replace(old_method, new_method)

# Also fix _post to use UTC time
content = content.replace(
    'created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")',
    'created_at=_dt.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")'
)

with open(r"C:\TenderAggregator\app\services\parsers\eis\client.py", "w", encoding="utf-8") as f:
    f.write(content)

print("OK")