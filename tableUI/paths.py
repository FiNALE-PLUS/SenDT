from pathlib import Path

from const import USER_DATA_PATH


def get_user_data_dir_for(song_id: int) -> Path:
    if not isinstance(song_id, int):
        raise TypeError(f'Song ID must be an integer (got {type(song_id)})')

    return USER_DATA_PATH / str(song_id)


def get_user_data_cover_art_dir_for(song_id: int) -> Path:
    return get_user_data_dir_for(song_id) / 'cover_art'


def get_user_data_chart_dir_for(song_id: int) -> Path:
    return get_user_data_dir_for(song_id) / 'chart'
