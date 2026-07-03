from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str = Field(default="default")


class ToolTraceEntry(BaseModel):
    tool: str
    args: dict
    result_summary: str


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    tool_trace: list[ToolTraceEntry] = Field(default_factory=list)
    properties: list[dict] = Field(default_factory=list)
