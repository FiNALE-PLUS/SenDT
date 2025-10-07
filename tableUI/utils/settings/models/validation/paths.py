from pathlib import Path
from typing import Annotated

from pydantic import AfterValidator


def existing_absolute_directory_validation(path: Path | None):
    if path is not None:
        if not isinstance(path, Path):
            raise TypeError(f"Expected Path but got {type(path)}")

        if not path.exists():
            raise ValueError("Path does not exist")
        if not path.is_dir():
            raise ValueError("Path is not a directory")

        return path.absolute()
    return path


optional_existing_absolute_directory = Annotated[Path | None, AfterValidator(existing_absolute_directory_validation)]