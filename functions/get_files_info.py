from pathlib import Path

__all__: list[str] = ["get_files_info"]


def get_files_info(working_directory: str, directory: str = ".", **kwargs) -> str:
    """Get information about files in a directory.
    
    Args:
        working_directory: The working directory path
        directory: Directory path to list (default: current directory)
        
    Returns:
        str: Formatted list of files with size and type information
    """
    working_dir: Path = Path(working_directory).resolve()
    target_dir: Path = (working_dir / directory).resolve()
    items: list[str] = [f"Result for {target_dir}"]
    try:
        target_dir.relative_to(working_dir)
        if not target_dir.is_dir():
            items.append(f'Error: "{directory}" is not a directory')

        for item in target_dir.iterdir():
            items.append(
                f"\t- {item.name}: file_size={item.lstat().st_size} bytes, is_dir={item.is_dir()}"
            )
    except ValueError:
        items.append(
            f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        )
    except FileNotFoundError:
        items.append(f"Error: Cannot list {directory} as it wasn't found")
    return "\n".join(items)
