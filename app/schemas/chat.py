from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class Message(BaseModel):
    """Chat message"""
    role: Literal["user", "assistant"] = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")

class ChatRequest(BaseModel):
    """Chat request schema"""
    messages: List[Message] = Field(..., description="Chat history")
    response_mode: Literal["freeform", "structured"] = Field(
        "freeform",
        description="Type of response format - conversational or structured"
    )
    stream: bool = Field(False, description="Whether to stream the response")

class ChatResponse(BaseModel):
    """Chat response schema"""
    message: Message = Field(..., description="Assistant's response message")
    sources: Optional[List[str]] = Field(None, description="Sources used to generate the response")

class SummarizationRequest(BaseModel):
    """Summarization request schema"""
    type: Literal["chapter", "character", "event","location","spell","house"] = Field(
        ...,
        description="Type of summarization to perform"
    )
    target: str = Field(..., description="Target to summarize (chapter name, character name, event name,location name , spell name, house name)")
    response_mode: Literal["freeform", "structured"] = Field(
        "structured",
        description="Type of response format - conversational or structured"
    )

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "ok"
    version: str