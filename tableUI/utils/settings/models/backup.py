from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, AfterValidator

from tableUI.utils.settings.models.validation.paths import existing_absolute_directory_validation, optionalExistingAbsoluteDirectory


class BackupSettings(BaseModel, validate_assignment=True):
    absolute_backup_path: optionalExistingAbsoluteDirectory = None
    audio: bool = True
    bg_videos: bool = True
    charts: bool = True
    cover_art: bool = True
