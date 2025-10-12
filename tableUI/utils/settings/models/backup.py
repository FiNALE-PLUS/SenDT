from pydantic import BaseModel

from tableUI.utils.settings.models.field_models.paths.existing_dir import optionalExistingAbsoluteDirectory


class BackupSettings(BaseModel, validate_assignment=True):
    absolute_backup_path: optionalExistingAbsoluteDirectory = None
    audio: bool = True
    bg_videos: bool = True
    charts: bool = True
    cover_art: bool = True
    tables: bool = True
