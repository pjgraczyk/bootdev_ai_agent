import os
import yaml
from typing import Dict, Callable, Type
from pathlib import Path
from langchain_core.tools import BaseTool
from pydantic import BaseModel

TOOL_REGISTRY: Dict[str, Callable[[], BaseTool]] = {}


def register_tool(tool_name: str):
    """Decorator to register a tool in the registry."""

    def decorator(func: Callable[[], BaseTool]):
        TOOL_REGISTRY[tool_name] = func
        return func

    return decorator


class Config(BaseModel):
    api_key: str
    temperature: float
    retries: int
    model: str
    verbose: bool
    tool_names: list[str] = []
    system_prompt: str
    tools: list[BaseTool] = []

    @classmethod
    def from_file(
        cls,
        tool_registry: Dict[str, Callable[[], BaseTool]],
        config_file: str = "agent_config.yaml",
    ):
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file {config_file} not found"
            )

        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
        config = cls.model_validate(config_data)
        config.tools = config._load_tools()

        return config

    def _load_tools(self) -> list[BaseTool]:
        tools = []
        for tool_name in self.tool_names:
            if tool_name in TOOL_REGISTRY:
                tools.append(TOOL_REGISTRY[tool_name]())
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        return tools
