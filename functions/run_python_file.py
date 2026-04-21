import subprocess
from typing import Type
from langchain_core.tools.structured import StructuredTool
from langchain_core.tools import InjectedToolArg, tool
from pathlib import Path
from typing import Annotated
from pydantic import BaseModel, Field
from typing import Optional

__all__: list[str] = ["run_python_file"]

class RunPythonFileSchema(BaseModel):
    file_path: str = Field(description="Path to the Python file to execute")
    args: Optional[list[str]] = Field(default=None, description="Optional list of command line arguments")


def run_python_file(
    file_path: str,
    args: list[str] | None = None,
    working_directory: str = ".",
) -> str:
    """Run a Python file with optional arguments.

    Args:
        file_path: Path to the Python file to execute
        args: Optional list of command line arguments to pass to the Python script
        working_directory: The working directory path (default: current directory)

    Returns:
        str: Execution results including stdout, stderr, and exit code
    """
    working_dir: Path = Path(working_directory).resolve()
    target_filepath: Path = (working_dir / file_path).resolve()
    items: list[str] = [f"Result for {target_filepath}"]
    try:
        target_filepath.relative_to(working_dir)
        if not target_filepath.is_file():
            items.append(
                f'Error: "{file_path}" does not exist or is not a regular file'
            )
        elif target_filepath.suffix != ".py":
            items.append(f'Error: "{file_path}" is not a Python file')
        else:
            command = ["python", target_filepath.absolute()]
            if args:
                command.extend(args)

            result = subprocess.run(
                command, capture_output=True, timeout=30, text=True
            )
            items.append(f"Process exited with code {result.returncode}")

            if result.stderr:
                items.append(f"STDERR: {result.stderr}")
            if result.stdout:
                items.append(f"STDOUT: {result.stdout}")
            if not result.stdout and not result.stderr:
                items.append("No output produced")
    except ValueError:
        items.append(
            f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        )
    except FileNotFoundError:
        items.append(f"Error: Cannot list {file_path} as it wasn't found")
    except Exception as e:
        items.append(f"Error: executing Python file: {e}")
    return "\n".join(items)


run_python_file_tool = StructuredTool.from_function(
    func=run_python_file,
    args_schema=RunPythonFileSchema,
    name="run_python_file",
    description="Executes a Python file with optional arguments",
)
