import shutil

from pydantic import ValidationError

from tableUI.const import SETTINGS_PATH
from tableUI.utils.settings.models.sendt_settings import SenDTSettings

def write_settings_to_database(settings: SenDTSettings):
    if not SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, 'w') as f:
            f.write(settings.model_dump_json(indent=2))

def write_default_settings_to_data():
    write_settings_to_database(SenDTSettings())

def get_sendt_settings() -> SenDTSettings:
    settings = None
    try:
        with open(SETTINGS_PATH, "r") as f:
            settings = SenDTSettings().model_validate_json(f.read())
    except FileNotFoundError:
        write_default_settings_to_data()
    except ValidationError:
        # Move invalid settings file using backup extension
        extension = '.json.bak'
        counter = 1
        backup_path = SETTINGS_PATH.with_suffix(extension)
        while backup_path.exists():
            if counter == 1000: # prevent infinite loops in worst case scenarios
                break
            counter += 1
            extension = f'.json.bak{counter}'
            backup_path = backup_path.with_suffix(extension)
        shutil.move(SETTINGS_PATH, backup_path)
        # Replace with default settings
        write_default_settings_to_data()
    finally:
        if settings is None:
            settings = SenDTSettings()

    return settings
