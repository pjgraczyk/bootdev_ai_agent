from pathlib import Path
from typing import Annotated

from langchain_core.tools import InjectedToolArg
from langchain_core.tools.structured import StructuredTool
from pydantic import BaseModel, Field

__all__: list[str] = ["write_file"]


class WriteFileSchema(BaseModel):
    file_path: str = Field(description="Path to the file to write")
    content: str = Field(description="Content to write to the file")


def write_file(
    working_directory: Annotated[str, InjectedToolArg] = ".",
    file_path: str = "",
    content: str = "",
) -> str:
    working_dir: Path = Path(working_directory).resolve()
    target_file: Path = (working_dir / file_path).resolve()

    try:
        target_file.relative_to(working_dir)
        if target_file.is_dir():
            return f'Error: Cannot write to "{file_path}" as it is a directory'
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

    except ValueError:
        return (
            f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        )
    except Exception as e:
        return f"Error: {e!s}"


write_file_tool = StructuredTool.from_function(
    func=write_file,
    name="write_file",
    description="Writes content to a file relative to the working directory",
)
