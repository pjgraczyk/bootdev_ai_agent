from config import register_tool, TOOL_REGISTRY
from functions import (
    get_file_content_tool,
    get_files_info_tool,
    write_file_tool,
    run_python_file_tool,
)


@register_tool("get_file_content_tool")
def _get_file_content_tool():
    return get_file_content_tool


@register_tool("get_files_info_tool")
def _get_files_info_tool():
    return get_files_info_tool


@register_tool("write_file_tool")
def _write_file_tool():
    return write_file_tool


@register_tool("run_python_file_tool")
def _run_python_file_tool():
    return run_python_file_tool
