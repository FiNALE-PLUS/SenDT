from pathlib import Path
from sys import platform

from PIL import Image

BASE_DIR = Path(__file__).resolve().parent

BINARY_DIR = BASE_DIR / 'bin'

if platform == 'win32':
    FFMPEG_NAME = 'ffmpeg.exe'
    FFPROBE_NAME = ('ffprobe'
                    '.exe')
# Intended for linux
else:
    FFMPEG_NAME = 'ffmpeg'
    FFPROBE_NAME = 'ffprobe'


FFMPEG_PATH = BINARY_DIR / FFMPEG_NAME
FFPROBE_PATH = BINARY_DIR / FFPROBE_NAME

DATA_PATH = BASE_DIR / 'data'
SETTINGS_PATH = DATA_PATH / 'settings.json'

BACKUP_PATH = DATA_PATH / 'backups'
USER_DATA_PATH = DATA_PATH / 'user_data'

# GENERATED_COVER_ART_PATH = BASE_DIR / 'data' / 'user' / 'img' / 'cover'
NO_COVER_IMG = Image.open(BASE_DIR / 'data' / 'img' / 'song_cover' / 'dummy.png')

FULL_COVER_ART_NAME = 'full.dds'
MIRROR_COVER_ART_NAME = 'mirror.dds'
SMALL_COVER_ART_NAME = 'small.dds'
