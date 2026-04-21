from tool_registry import TOOL_REGISTRY
from logger import SqliteLogger
from config import Config
from ai_agent import AIAgent
from cli_args import parse_arguments


def run_interactive_mode(
    agent: AIAgent, logger: SqliteLogger, initial_prompt: str
) -> None:
    prompt = initial_prompt
    while True:
        agent.process_interaction(prompt, logger)
        prompt = input("Enter another prompt (or 'exit' to quit): ")
        if prompt.lower() == "exit":
            break


def run_single_mode(agent: AIAgent, logger: SqliteLogger, prompt: str) -> None:
    agent.process_interaction(prompt, logger)


def main() -> None:
    args = parse_arguments()
    config = Config.from_file(TOOL_REGISTRY, args.config)

    if args.verbose:
        config.verbose = True

    logger = SqliteLogger()
    agent = AIAgent(config)

    if args.interactive:
        run_interactive_mode(agent, logger, args.user_prompt)
    else:
        run_single_mode(agent, logger, args.user_prompt)


if __name__ == "__main__":
    main()
