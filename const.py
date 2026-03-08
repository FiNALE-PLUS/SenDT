from pathlib import Path

from PIL import Image

from sys import platform

BASE_DIR = Path(__file__).resolve().parent

# TODO: Remove UI dirs when server is complete
UI_DIR = BASE_DIR / 'tableUI'

# TODO: replace single const with function to check for possible different exceptions
BINARY_DIR = BASE_DIR / 'bin'


if platform == 'win32':
    FFMPEG_NAME = 'ffmpeg.exe'
    FFPROBE_NAME = 'ffmpeg.exe'
# Intended for linux
else:
    FFMPEG_NAME = 'ffmpeg'
    FFPROBE_NAME = 'ffmpeg'

FFMPEG_PATH = BINARY_DIR / FFMPEG_NAME
FFPROBE_PATH = BINARY_DIR / FFPROBE_NAME

if not all((FFMPEG_PATH.is_file(), FFPROBE_PATH.is_file())):
    raise FileNotFoundError(
        f'Either FFmpeg or FFprobe have not been found. An FFmpeg executable is expected to be at {FFMPEG_PATH.absolute()}, and FFprobe at {FFPROBE_PATH.absolute()}'
    )

TEMP_DATA_PATH = BASE_DIR / 'tmp'
DATA_PATH = UI_DIR / 'data'
SETTINGS_PATH = UI_DIR / 'settings.json'

BACKUP_PATH = UI_DIR / 'backups'
USER_DATA_PATH = UI_DIR / 'user_data'

# GENERATED_COVER_ART_PATH = BASE_DIR / 'data' / 'user' / 'img' / 'cover'
NO_COVER_IMG = Image.open(UI_DIR / 'data' / 'img' / 'song_cover' / 'dummy.png')

FULL_COVER_ART_NAME = 'full.dds'
MIRROR_COVER_ART_NAME = 'mirror.dds'
SMALL_COVER_ART_NAME = 'small.dds'
