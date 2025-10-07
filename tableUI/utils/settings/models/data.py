from pydantic import BaseModel

from tableUI.utils.settings.models.validation.paths import optional_existing_absolute_directory


class DataSettings(BaseModel, validate_assignment=True):
    absolute_data_path: optional_existing_absolute_directory = None