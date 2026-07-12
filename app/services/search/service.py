import logging
from opensearchpy import OpenSearch
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

TENDER_MAPPING = {
    "properties": {
        "title": {"type": "text", "analyzer": "russian"},
        "description": {"type": "text", "analyzer": "russian"},
        "external_id": {"type": "keyword"},
        "source": {"type": "keyword"},
        "law": {"type": "keyword"},
        "status": {"type": "keyword"},
        "procurement_method": {"type": "keyword"},
        "region": {"type": "keyword"},
        "initial_price": {"type": "float"},
        "customer_name": {"type": "text"},
        "customer_inn": {"type": "keyword"},
        "okpd2_codes": {"type": "keyword"},
        "published_at": {"type": "date"},
        "submission_deadline": {"type": "date"},
    }
}


class SearchService:

    def __init__(self):
        self.client = OpenSearch(
            hosts=[f"http://{settings.opensearch_host}:{settings.opensearch_port}"],
        )
        self.index_name = settings.opensearch_index_tenders

    def ensure_index(self):
        if not self.client.indices.exists(index=self.index_name):
            self.client.indices.create(index=self.index_name, body={"mappings": TENDER_MAPPING})
            logger.info("Индекс %s создан", self.index_name)

    def index_tender(self, tender: dict):
        self.client.index(
            index=self.index_name,
            id=tender["id"],
            body=tender,
            refresh=False,
        )

    def index_tenders_bulk(self, tenders: list[dict]):
        from opensearchpy.helpers import bulk
        actions = [
            {
                "_index": self.index_name,
                "_id": t["id"],
                "_source": t,
            }
            for t in tenders
        ]
        success, errors = bulk(self.client, actions, refresh=False)
        return success, errors

    def search(self, query: str, filters: dict | None = None, size: int = 20, offset: int = 0):
        must = []
        if query:
            must.append({"multi_match": {"query": query, "fields": ["title^3", "description^2", "customer_name"]}})
        if filters:
            for field, value in filters.items():
                if value:
                    must.append({"term": {field: value}})

        body = {
            "query": {"bool": {"must": must}} if must else {"match_all": {}},
            "size": size,
            "from": offset,
            "sort": [{"published_at": {"order": "desc"}}],
        }

        return self.client.search(index=self.index_name, body=body)

    def close(self):
        self.client.close()
