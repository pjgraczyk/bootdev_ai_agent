from langchain_core.tools import BaseTool

from functions import (
    get_file_content_tool,
    get_files_info_tool,
    run_python_file_tool,
    write_file_tool,
)

TOOL_REGISTRY: dict[str, BaseTool] = {
    "get_file_content_tool": get_file_content_tool,
    "get_files_info_tool": get_files_info_tool,
    "write_file_tool": write_file_tool,
    "run_python_file_tool": run_python_file_tool,
}
