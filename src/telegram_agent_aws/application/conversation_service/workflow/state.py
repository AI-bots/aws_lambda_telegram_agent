from langgraph.graph import MessagesState


class TelegramAgentState(MessagesState):
    summary: str
    response_type: str
    audio_buffer: bytes
