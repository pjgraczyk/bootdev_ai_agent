from pathlib import Path

import yaml
from langchain_core.tools import BaseTool
from pydantic import BaseModel


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
        tool_registry: dict[str, BaseTool],
        config_file: str = "agent_config.yaml",
    ) -> "Config":
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file {config_file} not found",
            )

        with open(config_path) as f:
            config_data = yaml.safe_load(f)
        config = cls.model_validate(config_data)
        config.tools = config._load_tools(tool_registry)

        return config

    def _load_tools(self, tool_registry: dict[str, BaseTool]) -> list[BaseTool]:
        tools: list[BaseTool] = []
        for tool_name in self.tool_names:
            if tool_name in tool_registry:
                tools.append(tool_registry[tool_name])
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        return tools
