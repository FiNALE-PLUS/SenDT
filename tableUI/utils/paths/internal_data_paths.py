from pathlib import Path

from tableUI.const import USER_DATA_PATH


def get_internal_cover_art_paths_for_song_id(song_id: int) -> Path:
    return USER_DATA_PATH / str(song_id) / 'cover_art'


def get_internal_bg_video_path_for_song_id(song_id: int) -> Path:
    return USER_DATA_PATH / str(song_id) / 'bg_video' / 'bg.wmv'
