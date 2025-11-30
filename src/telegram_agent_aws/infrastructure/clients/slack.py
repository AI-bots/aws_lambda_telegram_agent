from functools import lru_cache

from slack_sdk import WebClient

from telegram_agent_aws.config import settings


@lru_cache(maxsize=1)
def get_slack_client() -> WebClient:
    """
    Get or create the Slack client singleton.
    The client is created once and cached for subsequent calls.
    """
    return WebClient(token=settings.SLACK_BOT_TOKEN)