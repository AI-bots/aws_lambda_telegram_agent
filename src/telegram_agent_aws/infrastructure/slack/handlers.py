import hashlib
import hmac
import json
import time

from slack_sdk import WebClient

from telegram_agent_aws.application.conversation_service.generate_response import get_agent_response
from telegram_agent_aws.config import settings
from telegram_agent_aws.infrastructure.clients.elevenlabs import get_elevenlabs_client
from telegram_agent_aws.infrastructure.clients.openai import get_openai_client
from telegram_agent_aws.infrastructure.clients.slack import get_slack_client

slack_client = get_slack_client()
openai_client = get_openai_client()
elevenlabs_client = get_elevenlabs_client()


def verify_slack_request(event: dict) -> bool:
    """
    Verify that the request came from Slack using the signing secret.
    """
    headers = event.get("headers", {})
    body = event.get("body", "")
    
    # Get Slack signature headers
    slack_signature = headers.get("x-slack-signature", "")
    slack_request_timestamp = headers.get("x-slack-request-timestamp", "")
    
    # Check timestamp to prevent replay attacks (within 5 minutes)
    if abs(time.time() - int(slack_request_timestamp)) > 60 * 5:
        return False
    
    # Create signature
    sig_basestring = f"v0:{slack_request_timestamp}:{body}"
    my_signature = "v0=" + hmac.new(
        settings.SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures
    return hmac.compare_digest(my_signature, slack_signature)


async def handle_slack_message(event_data: dict):
    """
    Handle incoming Slack message events.
    """
    event = event_data.get("event", {})
    
    # Ignore bot messages and message changed events
    if event.get("subtype") or event.get("bot_id"):
        return
    
    message_text = event.get("text", "")
    user_id = event.get("user")
    channel_id = event.get("channel")
    
    # Remove bot mention from message if present
    bot_user_id = event_data.get("authorizations", [{}])[0].get("user_id", "")
    if bot_user_id:
        message_text = message_text.replace(f"<@{bot_user_id}>", "").strip()
    
    if not message_text:
        return
    
    # Get agent response
    response = get_agent_response(
        {"messages": message_text},
        user_id=f"slack_{user_id}"
    )
    
    await send_slack_response(channel_id, response)


async def send_slack_response(channel_id: str, response: dict):
    """
    Send response back to Slack.
    """
    last_message = response["messages"][-1]
    content = last_message.content
    response_type = response.get("response_type", "text")
    
    if response_type == "text":
        slack_client.chat_postMessage(
            channel=channel_id,
            text=content
        )
    
    elif response_type == "audio":
        audio_bytes = response.get("audio_buffer")
        if audio_bytes:
            # Upload audio file to Slack
            slack_client.files_upload_v2(
                channel=channel_id,
                file=audio_bytes,
                filename="voice_message.mp3",
                title="Voice Message",
                initial_comment=content
            )
    else:
        slack_client.chat_postMessage(
            channel=channel_id,
            text="Sorry, I can't process that right now! 😔"
        )