from typing import Annotated

from pydantic import BaseModel, StringConstraints

from tableUI.utils.settings.models.field_models.paths.existing_dir import optionalExistingAbsoluteDirectory
from tableUI.utils.settings.models.field_models.paths.game_dir import optionalFinaleInstallDirectory


def validate_encryption_key(key: str):
    return key


DataEncryptionKey = Annotated[str, StringConstraints(pattern="^[0-9a-fA-F]{32}$")]


class DataSettings(BaseModel, validate_assignment=True):
    absolute_data_path: optionalExistingAbsoluteDirectory = None
    default_game_path: optionalFinaleInstallDirectory = None
    crypt_keys: dict[str, DataEncryptionKey] = {}

