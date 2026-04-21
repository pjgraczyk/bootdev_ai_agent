from langchain_core.tools import BaseTool
from pydantic import BaseModel
from langchain_core.messages import BaseMessage


class Config(BaseModel):
    api_key: str
    temperature: float
    retries: int
    model: str
    messages: list[BaseMessage]
    verbose: bool
    tools: list[BaseTool]
    system_prompt: str
