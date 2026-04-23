from logger import MetadataDict
from langchain_core.runnables.config import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_mistralai import ChatMistralAI
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from config import Config
from logger import Logger


class AIAgent:
    def __init__(self, config: Config) -> None:
        self.llm = ChatMistralAI(
            model=config.model,
            api_key=config.api_key,
            temperature=config.temperature,
            max_retries=config.retries,
        )
        self.memory = MemorySaver()
        self.agent = create_agent(self.llm, tools=config.tools, checkpointer=self.memory)
        self.thread_id = "default"
        self.system_prompt = config.system_prompt
        self.verbose = config.verbose
        self.console = Console()

    def get_user_input(self) -> str:
        return Prompt.ask("Enter your prompt", default="[dim] Enter text here [/dim]")

    def process_interaction(self, prompt: str, logger: Logger) -> None:
        config: RunnableConfig = {"configurable": {"thread_id": self.thread_id}}
        seen = 0
        for state in self.agent.stream(
            {"messages": [HumanMessage(content=prompt)]},
            config=config,
            stream_mode="values",
        ):
            messages = state["messages"]
            for msg in messages[seen:]:
                if self.verbose:
                    print(msg)
                if isinstance(msg, AIMessage) and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        self.console.print(
                            f"[yellow]Calling function: {tool_call['name']}({tool_call['args']})[/yellow]"
                        )
                    if msg.usage_metadata:
                        log_metadata = MetadataDict(
                            input_tokens=msg.usage_metadata.get("input_tokens", 0),
                            output_tokens=msg.usage_metadata.get("output_tokens", 0),
                            model_name=msg.response_metadata.get("model_name", ""),
                        )
                        if log_metadata:
                            logger.log_interaction(prompt, msg, log_metadata)
                elif isinstance(msg, ToolMessage) and msg.content:
                    self.console.print(
                        Panel(str(msg.content), title="Tool Result", border_style="cyan")
                    )
                elif isinstance(msg, AIMessage) and msg.content:
                    self.console.print(Panel(Markdown(str(msg.content)), border_style="green"))
            seen = len(messages)
