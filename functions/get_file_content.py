from pathlib import Path

__all__: list[str] = ["get_file_content"]


def get_file_content(working_directory: str, file_path: str, **kwargs) -> str:
    """Get the content of a file.
    
    Args:
        working_directory: The working directory path
        file_path: Path to the file to read
        
    Returns:
        str: File content (truncated if exceeds 10000 characters)
    """
    working_dir: Path = Path(working_directory).resolve()
    target_file: Path = (working_dir / file_path).resolve()
    
    try:
        target_file.relative_to(working_dir)
        
        if not target_file.is_file():
            return f'Error: File not found or is not a regular file: "{file_path}"'
        
        MAX_CHARS = 10000
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read(MAX_CHARS)
            if f.read(1):
                content += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
        return content
        
    except ValueError:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    except Exception as e:
        return f'Error: {str(e)}'
