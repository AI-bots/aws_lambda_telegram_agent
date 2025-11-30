from functools import lru_cache

from elevenlabs.client import ElevenLabs

from telegram_agent_aws.config import settings


@lru_cache(maxsize=1)
def get_elevenlabs_client() -> ElevenLabs:
    """
    Get or create the ElevenLabs client singleton.
    The client is created once and cached for subsequent calls.
    """
    return ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
