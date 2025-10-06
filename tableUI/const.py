from pathlib import Path

from PIL import Image

BASE_DIR = Path(__file__).resolve().parent

BINARY_DIR = BASE_DIR / 'bin'
FFMPEG_PATH = BINARY_DIR / 'ffmpeg.exe'

DATA_PATH = BASE_DIR / 'data'
BACKUP_PATH = DATA_PATH / 'backups'
USER_DATA_PATH = DATA_PATH / 'user_data'

# GENERATED_COVER_ART_PATH = BASE_DIR / 'data' / 'user' / 'img' / 'cover'
NO_COVER_IMG = Image.open(BASE_DIR / 'data' / 'img' / 'song_cover' / 'dummy.png')

FULL_COVER_ART_NAME = 'full.dds'
MIRROR_COVER_ART_NAME = 'mirror.dds'
SMALL_COVER_ART_NAME = 'small.dds'
