from argparse import ArgumentParser, Namespace


def parse_arguments() -> Namespace:
    parser = ArgumentParser(description="AI Coding Agent")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Enable interactive mode"
    )
    parser.add_argument(
        "--config", default="agent_config.yaml", help="Path to config file"
    )
    return parser.parse_args()
