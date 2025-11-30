from functools import lru_cache

from qdrant_client import QdrantClient

from telegram_agent_aws.config import settings


@lru_cache(maxsize=1)
def get_qdrant_client():
    return QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
    )
