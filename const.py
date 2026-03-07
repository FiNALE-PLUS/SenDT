from pathlib import Path

from PIL import Image

BASE_DIR = Path(__file__).resolve().parent

# TODO: Remove UI dirs when server is complete
UI_DIR = BASE_DIR / 'tableUI'

# TODO: replace single const with function to check for possible different exceptions
BINARY_DIR = BASE_DIR / 'bin'
FFMPEG_PATH = BINARY_DIR / 'ffmpeg.exe'
FFPROBE_PATH = BINARY_DIR / 'ffprobe.exe'

DATA_PATH = UI_DIR / 'data'
SETTINGS_PATH = UI_DIR / 'settings.json'

BACKUP_PATH = UI_DIR / 'backups'
USER_DATA_PATH = UI_DIR / 'user_data'

# GENERATED_COVER_ART_PATH = BASE_DIR / 'data' / 'user' / 'img' / 'cover'
NO_COVER_IMG = Image.open(UI_DIR / 'data' / 'img' / 'song_cover' / 'dummy.png')

FULL_COVER_ART_NAME = 'full.dds'
MIRROR_COVER_ART_NAME = 'mirror.dds'
SMALL_COVER_ART_NAME = 'small.dds'
