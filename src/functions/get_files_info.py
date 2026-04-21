from langchain_core.tools.structured import StructuredTool
from pathlib import Path
from pydantic import BaseModel, Field

__all__: list[str] = ["get_files_info"]


class GetFilesInfoSchema(BaseModel):
    directory: str = Field(default=".", description="Directory path to list")


def get_files_info(directory: str = ".", working_directory: str = ".") -> str:
    """Get information about files in a directory.

    Args:
        directory: Directory path to list (default: current directory)
        working_directory: The working directory path (default: current directory)

    Returns:
        str: Formatted list of files with size and type information
    """
    working_dir = Path(working_directory).resolve()
    target_dir = (working_dir / directory).resolve()
    items = [f"Result for {target_dir}"]
    try:
        if not target_dir.is_relative_to(working_dir):
            items.append(
                f'Error: "{directory}" is outside the permitted directory'
            )
            return "\n".join(items)

        if not target_dir.exists():
            items.append(f'Error: "{directory}" does not exist')
        elif not target_dir.is_dir():
            items.append(f'Error: "{directory}" is a file, not a directory')
        else:
            for item in target_dir.iterdir():
                stats = item.lstat()
                items.append(
                    f"\t- {item.name}: size={stats.st_size} bytes, is_dir={item.is_dir()}"
                )

    except PermissionError:
        items.append(f"Error: Permission denied for {directory}")
    except Exception as e:
        items.append(f"Error: {str(e)}")

    return "\n".join(items)


get_files_info_tool = StructuredTool.from_function(
    func=get_files_info,
    args_schema=GetFilesInfoSchema,
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
)
