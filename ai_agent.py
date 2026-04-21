from typing import Any
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from config import Config


class AIAgent:
    def __init__(self, config: Config):
        self.llm = ChatMistralAI(
            model=config.model,
            api_key=config.api_key,
            temperature=config.temperature,
            max_retries=config.retries,
        )
        self.agent = create_agent(self.llm, tools=config.tools)
        self.messages = config.messages
        self.verbose = config.verbose

    def add_prompt(self, message: str) -> HumanMessage:
        user_message: HumanMessage = HumanMessage(content=message)
        self.messages.append(user_message)
        return user_message

    def invoke_prompt(self) -> AIMessage:
        ai_response: Any = self.agent.invoke({"messages": self.messages})
        self.messages.append(ai_response)
        return ai_response

    def print_response(self, response) -> None:
        console = Console()
        messages = response.get("messages", [])

        for msg in messages:
            if type(msg) == AIMessage:
                if msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        tool_name = tool_call.get("name", "unknown")
                        tool_args = tool_call.get("args", {})
                        console.print(f"Calling function: {tool_name}({tool_args})")

                if msg.content:
                    console.print("Response:", style="bold blue")
                    console.print(Panel(Markdown(msg.content), border_style="green"))
