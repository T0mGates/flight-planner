# main.py or wherever your models are
from pydantic import BaseModel
from typing import List, Optional, Any # Add Any here
from openai import AsyncOpenAI       # Use the Async version
import os

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    history: List[ChatMessage]
    new_message: str
    scheduling_data: Optional[Any] = None 