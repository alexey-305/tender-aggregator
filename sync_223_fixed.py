"""
Точка входа для синхронизации извещений из ЕИС в нашу БД.
"""

import argparse
import asyncio
import io
import logging
import zipfile
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.db.session import async_session_maker
from app.models.customer import Customer
from app.models.enums import ProcurementLaw, TenderSource, TenderStatus
from app.models.tender import Tender
from app.services.parsers.eis.client import EISClient, EISClientError
from app.services.parsers.eis.document_types import DEFAULT_DOCUMENT_TYPES, NOTIFICATION_SUBSYSTEM_TYPE
from app.services.parsers.eis.xml_mapper import ParsedNotification, parse_notification_xml

logger = logging.getLogger(__name__)


def _extract_xml_files(archive_bytes: bytes) -> list[bytes]:
    xml_files: list[bytes] = []
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as outer_zip:
        for name in outer_zip.namelist():
            if name.lower().endswith(".xml"):
                xml_files.append(outer_zip.read(name))
            elif name.lower().endswith(".zip"):
                try:
                    with zipfile.ZipFile(io.BytesIO(outer_zip.read(name))) as inner_zip:
                        for inner_name in inner_zip.namelist():
                            if inner_name.lower().endswith(".xml"):
                                xml_files.append(inner_zip.read(inner_name))
                except zipfile.BadZipFile:
                    logger.warning("Cannot unpack nested archive %s", name)
    return xml_files


async def _get_or_create_customer(session, inn: str | None, name: str | None) -> Customer | None:
    if not inn and not name:
        return None
    if inn:
        result = await session.execute(select(Customer).where(Customer.inn == inn))
        existing = result.scalar_one_or_none()
        if existing:
            return existing
    customer = Customer(inn=inn, name=name or f"Customer INN {inn}")
    session.add(customer)
    await session.flush()
    return customer


async def _upsert_tender(session, parsed: ParsedNotification, region: str, law: str = "44-fz") -> None:
    customer = await _get_or_create_customer(session, parsed.customer_inn, parsed.customer_name)

    source = TenderSource.EIS_44FZ if law == "44-fz" else TenderSource.EIS_223FZ
    law_enum = ProcurementLaw.FZ_44 if law == "44-fz" else ProcurementLaw.FZ_223

    values = dict(
        source=source,
        external_id=parsed.external_id,
        law=law_enum,
        title=parsed.title,
        okpd2_codes=parsed.okpd2_codes,
        procurement_method=parsed.procurement_method,
        status=parsed.status,
        customer_id=customer.id if customer else None,
        initial_price=parsed.initial_price,
        region=region,
        published_at=parsed.published_at,
        submission_deadline=parsed.submission_deadline,
        summarizing_date=parsed.summarizing_date,
        raw_data=parsed.raw_data,
    )

    stmt = pg_insert(Tender).values(**values)
    update_cols = {k: v for k, v in values.items() if k not in ("source", "external_id")}
    stmt = stmt.on_conflict_do_update(
        constraint="uq_tender_source_external_id",
        set_=update_cols,
    )
    await session.execute(stmt)


async def sync_region_date(
    region: str,
    exact_date: date,
    document_types: list[str] | None = None,
    token: str | None = None,
    subsystem_type: str = NOTIFICATION_SUBSYSTEM_TYPE,
    law_type: str = "44",
) -> dict[str, int]:
    document_types = document_types or DEFAULT_DOCUMENT_TYPES
    client = EISClient(token=token)
    stats = {"requested": 0, "downloaded": 0, "parsed": 0, "saved": 0, "errors": 0}

    async with async_session_maker() as session:
        for document_type in document_types:
            stats["requested"] += 1
            try:
                if law_type == "223":
                    archive_ref = client.request_archive_223(
                        org_region=region,
                        exact_date=exact_date,
                        document_type=document_type,
                    )
                else:
                    archive_ref = client.request_archive(
                        org_region=region,
                        exact_date=exact_date,
                        document_type=document_type,
                        subsystem_type=subsystem_type,
                    )
                archive_bytes = client.download_archive(archive_ref)
                stats["downloaded"] += 1
            except EISClientError as exc:
                logger.warning("Skipping %s for %s (region %s): %s", document_type, exact_date, region, exc)
                stats["errors"] += 1
                continue

            xml_files = _extract_xml_files(archive_bytes)
            for xml_bytes in xml_files:
                parsed = parse_notification_xml(xml_bytes, document_type)
                if parsed is None:
                    continue
                stats["parsed"] += 1
                try:
                    await _upsert_tender(session, parsed, region, law=law_type)
                    stats["saved"] += 1
                except Exception:
                    logger.exception("Failed to save tender %s", parsed.external_id)
                    stats["errors"] += 1

        await session.commit()

    return stats


def _cli() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Sync notifications from EIS")
    parser.add_argument("--region", required=True, help="Region code, e.g. 77 (Moscow)")
    parser.add_argument("--date", required=True, help="Date in YYYY-MM-DD format")
    parser.add_argument("--token", default=None, help="EIS token")
    args = parser.parse_args()

    exact_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    stats = asyncio.run(sync_region_date(region=args.region, exact_date=exact_date, token=args.token))
    logger.info("Done: %s", stats)


if __name__ == "__main__":
    _cli()