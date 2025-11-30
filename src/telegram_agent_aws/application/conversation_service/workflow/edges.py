from typing import Literal

from langgraph.graph import END

from telegram_agent_aws.application.conversation_service.workflow.state import TelegramAgentState


def should_summarize_conversation(state: TelegramAgentState) -> Literal["summarize_conversation_node", END]:
    messages = state["messages"]

    if len(messages) > 30:
        return "summarize_conversation_node"

    return END
