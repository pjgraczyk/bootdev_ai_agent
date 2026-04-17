from pathlib import Path

__all__: list[str] = ["get_file_content"]


def get_file_content(working_directory: str, file_path: str) -> str:
    working_dir: Path = Path(working_directory).resolve()
    target_file: Path = (working_dir / file_path).resolve()
    
    try:
        # Validate path is within working directory
        target_file.relative_to(working_dir)
        
        # Check if it's a regular file
        if not target_file.is_file():
            return f'Error: File not found or is not a regular file: "{file_path}"'
        
        # Read file with truncation
        MAX_CHARS = 10000
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read(MAX_CHARS)
            if f.read(1):  # Check if there's more content
                content += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
        
        return content
        
    except ValueError:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    except Exception as e:
        return f'Error: {str(e)}'
