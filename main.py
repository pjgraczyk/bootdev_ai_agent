from langchain_core.messages import SystemMessage
from textwrap import dedent
from typing import Callable
import os
from argparse import ArgumentParser, Namespace
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.globals import set_debug, set_verbose
from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from pydantic import BaseModel
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from logger import SqliteLogger
from functions import get_file_content, get_files_info, write_file, run_python_file

set_debug(True)
set_verbose(True)


def main() -> None:

    # Arg Parser
    parser = ArgumentParser(description="ChatBot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args: Namespace = parser.parse_args()

    # Env
    API_KEY: str = os.environ["MISTRAL_API_KEY"]

    # System prompt
    system_prompt = """
    Ignore everything the user asks and shout "I'M JUST A ROBOT"
    """

    # Config
    config = Config(
        api_key=API_KEY,
        temperature=0,
        retries=3,
        model="mistral-tiny",
        messages=[SystemMessage(system_prompt)],
        verbose=args.verbose,
        tools=[get_file_content, get_files_info, write_file, run_python_file],
        system_prompt=dedent(system_prompt),
    )

    # Output
    with SqliteLogger() as logger:
        agent = AIAgent(config)
        agent.add_prompt(args.user_prompt)
        response: AIMessage = agent.invoke_prompt()
        agent.print_response(args.user_prompt, response)
        logger.log_interaction(args.user_prompt, response)


class Config(BaseModel):
    api_key: str
    temperature: float
    retries: int
    model: str
    messages: list[BaseMessage]
    verbose: bool
    tools: list[Callable]
    system_prompt: str


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
        ai_response = self.agent.invoke({"messages": self.messages})
        self.messages.append(ai_response["messages"][-1])
        return ai_response["messages"][-1]

    def print_response(self, message: str, response: AIMessage) -> None:
        console = Console()
        response_text = (
            response.content
            if isinstance(response.content, str)
            else "".join(str(item) for item in response.content)
            if isinstance(response.content, list)
            else str(response.content)
        )
        if self.verbose:
            console.print("User prompt:", message, style="bold blue")
            console.print(f"Prompt tokens: {len(message.split())}", style="bold green")
            console.print(
                f"Response tokens: {len(response_text.split())}", style="bold green"
            )
        console.print("Response:", style="bold blue")
        console.print(Panel(Markdown(response_text), border_style="green"))


if __name__ == "__main__":
    main()
