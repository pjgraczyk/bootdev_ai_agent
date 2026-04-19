import os
from pathlib import Path

__all__: list[str] = ["write_file"]


def write_file(working_directory: str, file_path: str, content: str, **kwargs) -> str:
    """Write content to a file.
    
    Args:
        working_directory: The working directory path
        file_path: Path to the file to write
        content: Content to write to the file
        
    Returns:
        str: Success message or error description
    """
    working_dir: Path = Path(working_directory).resolve()
    target_file: Path = (working_dir / file_path).resolve()
    
    try:
        # Validate path is within working directory
        target_file.relative_to(working_dir)
        
        # Check if it's a directory
        if target_file.is_dir():
            return f'Error: Cannot write to "{file_path}" as it is a directory'
        
        # Create parent directories if they don't exist
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content to file
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        
    except ValueError:
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    except Exception as e:
        return f'Error: {str(e)}'
