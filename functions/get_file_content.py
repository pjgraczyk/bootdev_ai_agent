from typing import Type
from langchain_core.tools.structured import StructuredTool
from langchain_core.tools import InjectedToolArg, tool
from pathlib import Path
from typing import Annotated
from pydantic import BaseModel, Field

__all__: list[str] = ["get_file_content"]

class GetFileContentSchema(BaseModel):
    file_path: str = Field(description="Path to the file to read")


def get_file_content(file_path: str, working_directory: str = ".") -> str:
    """Get the content of a file.

    Args:
        file_path: Path to the file to read
        working_directory: The working directory path (default: current directory)

    Returns:
        str: File content (truncated if exceeds 10000 characters)
    """
    working_dir: Path = Path(working_directory).resolve()
    target_file: Path = (working_dir / file_path).resolve()

    try:
        target_file.relative_to(working_dir)

        if not target_file.is_file():
            return (
                f'Error: File not found or is not a regular file: "{file_path}"'
            )

        MAX_CHARS = 10000
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read(MAX_CHARS)
            if f.read(1):
                content += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
        return content

    except ValueError:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    except Exception as e:
        return f"Error: {str(e)}"


get_file_content_tool = StructuredTool.from_function(
    func=get_file_content,
    args_schema=GetFileContentSchema,
    name="get_file_content",
    description="Reads the content of a file relative to the working directory",
)
