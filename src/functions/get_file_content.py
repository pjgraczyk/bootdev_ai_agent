from langchain_core.tools.structured import StructuredTool
from pathlib import Path
from pydantic import BaseModel, Field

__all__: list[str] = ["get_file_content"]


class GetFileContentSchema(BaseModel):
    file_path: str = Field(description="Path to the file to read")


def get_file_content(
    working_directory: str = ".", file_path: str | None = None
) -> str:
    if file_path is None:
        return "Error: file_path parameter is required"

    working_dir: Path = Path(working_directory).resolve()
    target_file: Path = (working_dir / file_path).resolve()

    try:
        target_file.relative_to(working_dir)

        if not target_file.is_file():
            return (
                f'Error: File not found or is not a regular file: "{file_path}"'
            )

        MAX_CHARS = 10000
        text = target_file.read_text("utf-8")
        if len(text) >= MAX_CHARS:
            text = (
                text[:MAX_CHARS]
                + f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
            )
        return text

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
