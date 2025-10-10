from pydantic import BaseModel

from tableUI.utils.settings.models.backup import BackupSettings
from tableUI.utils.settings.models.data import DataSettings


class SenDTSettings(BaseModel):
    backup: BackupSettings = BackupSettings()
    data: DataSettings = DataSettings()