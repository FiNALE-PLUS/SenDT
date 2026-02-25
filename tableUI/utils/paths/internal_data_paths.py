from pathlib import Path

from tableUI.const import USER_DATA_PATH
from tableUI.db.models import Song, Chart


def get_internal_cover_art_paths_for_song_id(song_id: int) -> Path:
    return USER_DATA_PATH / str(song_id) / 'cover_art'


def get_internal_bg_video_path_for_song_id(song_id: int) -> Path:
    return USER_DATA_PATH / str(song_id) / 'bg_video' / 'bg.wmv'

def get_internal_song_chart_dir(song: Song) -> Path:
    # Force 4 digit width for future-proofing
    return USER_DATA_PATH / 'charts' / f'{song.id}'

def get_internal_chart_path(chart: Chart):
    return get_internal_song_chart_dir(chart.chart_song) / f'{chart.difficulty_level_id}.sdb'