from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    BaseMessage,
    SystemMessage,
)
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages.utils import filter_messages
from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.live import Live
from rich.spinner import Spinner
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
        self.verbose = config.verbose
        self.console = Console()
        self.message_history = InMemoryChatMessageHistory()
        self.message_history.add_message(
            SystemMessage(content=config.system_prompt)
        )

    def add_prompt(self, message: str) -> HumanMessage:
        user_message = HumanMessage(content=message)
        self.message_history.add_message(user_message)
        return user_message

    def get_user_input(self) -> str:
        return Prompt.ask(
            "Enter your prompt", default="[dim] Enter text here [/dim]"
        )

    def _show_tool_calls(self, messages: list[BaseMessage]) -> None:
        for msg in messages:
            match msg:
                case AIMessage(tool_calls=tool_calls) if tool_calls:
                    for tool_call in tool_calls:
                        tool_name = tool_call["name"]
                        tool_args = tool_call["args"]
                        self.console.print(
                            f"[yellow]Calling function: {tool_name}({tool_args})[/yellow]"
                        )
                case _:
                    continue

    def invoke_prompt(self) -> AIMessage:
        with Live(Spinner("dots", text="Thinking..."), refresh_per_second=10):
            messages = self.message_history.messages

            result = self.agent.invoke({"messages": messages})
            match result:
                case {"messages": result_messages}:
                    ai_response = result_messages[-1]
                    self._show_tool_calls(result_messages)
                case _:
                    ai_response = result

        # Cast to AIMessage to satisfy type checker
        ai_response_cast = AIMessage(
            content=str(ai_response.content)
            if hasattr(ai_response, "content")
            else str(ai_response)
        )
        self.message_history.add_message(ai_response_cast)
        return ai_response_cast

    def print_response(self, response: AIMessage) -> None:
        match response:
            case AIMessage(tool_calls=tool_calls) if tool_calls:
                for tool_call in tool_calls:
                    tool_name = tool_call.get("name", "unknown")
                    tool_args = tool_call.get("args", {})
                    self.console.print(
                        f"[yellow]Calling function: {tool_name}({tool_args})[/yellow]"
                    )
            case _:
                pass

        if response.content:
            self.console.print("Response:", style="bold blue")
            content_str = str(response.content) if response.content else ""
            self.console.print(
                Panel(Markdown(content_str), border_style="green")
            )

    def process_interaction(self, prompt: str, logger) -> None:
        self.add_prompt(prompt)
        response = self.invoke_prompt()
        self.print_response(response)
        logger.log_interaction(prompt, response)

    def get_message_history(self) -> list[BaseMessage]:
        """Get all messages in chronological order."""
        return self.message_history.messages

    def get_user_messages(self) -> list[HumanMessage]:
        """Get all user messages using built-in filter_messages."""
        return [
            msg
            for msg in filter_messages(
                self.message_history.messages, include_types="human"
            )
            if isinstance(msg, HumanMessage)
        ]

    def get_ai_messages(self) -> list[AIMessage]:
        """Get all AI messages using built-in filter_messages."""
        return [
            msg
            for msg in filter_messages(
                self.message_history.messages, include_types="ai"
            )
            if isinstance(msg, AIMessage)
        ]

    def get_system_messages(self) -> list[BaseMessage]:
        """Get all system messages using built-in filter_messages."""
        return filter_messages(
            self.message_history.messages, include_types="system"
        )
