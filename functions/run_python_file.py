import subprocess
from pathlib import Path

__all__: list[str] = ['run_python_file']

def run_python_file(working_directory: str, file_path: str, args: list[str] | None = None):
    working_dir: Path = Path(working_directory).resolve()
    target_filepath: Path = (working_dir / file_path).resolve()
    items: list[str] = [f"Result for {target_filepath}"]
    try:
        target_filepath.relative_to(working_dir)
        if not target_filepath.is_file():
            items.append(f'Error: "{file_path}" does not exist or is not a regular file')
        if target_filepath.suffix != '.py':
            items.append(f'Error: "{file_path}" is not a Python file')
        command = ['python', target_filepath.absolute()]
        if args:
            command.extend(args)
        result = subprocess.run(command, capture_output=True)
        print(result)
    except ValueError:
        items.append(
            f'Error: Cannot list "{target_filepath}" as it is outside the permitted working directory'
        )
    except FileNotFoundError:
        items.append(f"Error: Cannot list {target_filepath} as it wasn't found")
    return "\n".join(items)
