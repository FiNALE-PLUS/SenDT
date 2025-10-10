from typing import Annotated

from pydantic import BaseModel, AfterValidator, StringConstraints

from tableUI.utils.settings.models.validation.paths import optionalExistingAbsoluteDirectory


def validate_encryption_key(key: str):
    return key


DataEncryptionKey = Annotated[str, StringConstraints(pattern="^[0-9a-fA-F]{32}$")]


class DataSettings(BaseModel, validate_assignment=True):
    absolute_data_path: optionalExistingAbsoluteDirectory = None
    crypt_keys: dict[str, DataEncryptionKey] = {}

