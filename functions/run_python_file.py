import subprocess
from pathlib import Path

__all__: list[str] = ["run_python_file"]


def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None, **kwargs
) -> str:
    """Run a Python file with optional arguments.

    Args:
        working_directory: The working directory path
        file_path: Path to the Python file to execute
        args: Optional list of command line arguments to pass to the Python script

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

            result = subprocess.run(command, capture_output=True, timeout=30, text=True)
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
