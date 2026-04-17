from langchain_core.messages import BaseMessage
from logger import SqliteLogger
import os
import sqlite3
from pydantic import BaseModel
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, AIMessage
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from argparse import ArgumentParser
from argparse import Namespace

def main() -> None:

    # Arg Parser
    parser = ArgumentParser(description='ChatBot')
    parser.add_argument('user_prompt', type=str, help='User prompt')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args: Namespace = parser.parse_args()
    
    # Env
    API_KEY: str = os.environ["MISTRAL_API_KEY"]

    # Config
    config = Config(
        api_key=API_KEY,
        temperature=0.7,
        retries=3,
        model="mistral-tiny",
        messages=[],
        verbose=args.verbose,
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

class AIAgent:
    def __init__(self, config: Config):
        self.llm = ChatMistralAI(
            model=config.model,
            api_key=config.api_key,
            temperature=config.temperature,
            max_retries=config.retries,
        )
        self.messages = config.messages
        self.verbose = config.verbose

    def add_prompt(self, message: str) -> HumanMessage:
        user_message: HumanMessage = HumanMessage(content=message)
        self.messages.append(user_message)
        return user_message

    def invoke_prompt(self) -> AIMessage:
        ai_response: AIMessage = self.llm.invoke(self.messages)
        self.messages.append(ai_response)
        return ai_response

    def print_response(self, message: str, response: AIMessage) -> None:
        console = Console()
        if self.verbose:
            console.print("User prompt:", message, style="bold blue")
            console.print(f"Prompt tokens: {len(message.split())}", style="bold green")
            console.print(f"Response tokens: {len(response.content.split())}", style="bold green")
        console.print("Response:", style="bold blue")
        console.print(Panel(Markdown(response.content), border_style="green"))

if __name__ == "__main__":
    main()
