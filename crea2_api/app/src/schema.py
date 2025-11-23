from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Any, List, Union


class Query(BaseModel):
    """Query schema for the invoke endpoint"""

    input: str = Field(description="The user query to the chatbot")
    session_id: str = Field(
        description="A UUID which identifies this conversation over the chat storage"
    )


class Response(BaseModel):
    """Final response schema to the question being asked"""

    answer: str = Field(description="The final answer to the user query.")
    sources: List[str] = Field(
        description="List of uuid that contain answer to the question. Only include an uuid if it contains relevant information."
    )
