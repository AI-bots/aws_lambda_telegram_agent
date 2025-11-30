import asyncio
import json

from telegram_agent_aws.infrastructure.slack.handlers import handle_slack_message, verify_slack_request


async def process_slack_event(event_data: dict):
    """
    Process Slack events asynchronously.
    """
    event_type = event_data.get("type")
    
    # Handle URL verification challenge
    if event_type == "url_verification":
        return {
            "statusCode": 200,
            "body": json.dumps({"challenge": event_data.get("challenge")})
        }
    
    # Handle event callbacks
    if event_type == "event_callback":
        try:
            await handle_slack_message(event_data)
        except Exception as e:
            print(f"Error processing Slack message: {e}")
            import traceback
            traceback.print_exc()
    
    return {"statusCode": 200, "body": json.dumps({"ok": True})}


def slack_lambda_handler(event, context):
    """
    AWS Lambda handler for Slack webhook.
    
    The event contains the API Gateway payload with the Slack event in the body.
    """
    print("**Slack Event received**")
    print(json.dumps(event, indent=2))
    
    try:
        # Verify request is from Slack
        if not verify_slack_request(event):
            print("Invalid Slack signature")
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "Invalid signature"})
            }
        
        body = event.get("body", "{}")
        
        if isinstance(body, str):
            event_data = json.loads(body)
        else:
            event_data = body
        
        print("**Parsed Slack event data**")
        print(json.dumps(event_data, indent=2))
        
        # Process event
        result = asyncio.run(process_slack_event(event_data))
        
        return result
    
    except Exception as e:
        print(f"Error in slack_lambda_handler: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "statusCode": 500,
            "body": json.dumps({"ok": False, "error": str(e)})
        }