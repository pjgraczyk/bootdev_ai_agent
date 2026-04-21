import os
from langchain_core.messages import SystemMessage
from textwrap import dedent
from argparse import ArgumentParser, Namespace
from langchain_core.messages import AIMessage
from langchain_core.globals import set_debug, set_verbose
from logger import SqliteLogger
from functions import (
    get_file_content_tool,
    get_files_info_tool,
    write_file_tool,
    run_python_file_tool,
)
from config import Config
from ai_agent import AIAgent

set_debug(False)
set_verbose(False)


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
    You are a helpful AI coding agent.

    When a user asks any question or makes any request, make a function call plan. You can perform the following operations:

    - List files and directories

    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
    """

    # Config
    config = Config(
        api_key=API_KEY,
        temperature=0,
        retries=3,
        model="mistral-tiny",
        messages=[SystemMessage(system_prompt)],
        verbose=args.verbose,
        tools=[
            get_file_content_tool,
            get_files_info_tool,
            write_file_tool,
            run_python_file_tool,
        ],
        system_prompt=dedent(system_prompt),
    )

    # Output
    with SqliteLogger() as logger:
        agent = AIAgent(config)
        agent.add_prompt(args.user_prompt)
        response: AIMessage = agent.invoke_prompt()
        agent.print_response(response)
        logger.log_interaction(args.user_prompt, response)


if __name__ == "__main__":
    main()
