from functools import lru_cache

from pymongo import MongoClient

from telegram_agent_aws.config import settings


@lru_cache(maxsize=1)
def get_mongodb_client():
    return MongoClient(settings.MONGODB_CONNECTION_STRING)
