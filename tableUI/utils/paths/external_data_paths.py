from pathlib import Path
from typing import NamedTuple

from db.models import Song, Chart
from tableUI.parsers.tables.field_types.quoted_string import DoubleQuotedString


class CoverArtPaths(NamedTuple):
    full_size: Path
    mirror_effect: Path
    small: Path


class TablePaths(NamedTuple):
    music: Path
    score: Path
    fes_list: Path
    textout_ex: Path
    textout_jp: Path


def get_table_dir(path: Path):
    return path / 'data' / 'tables'


def get_chart_dir(path: Path):
    return path / 'data' / 'score'


def get_encrypted_table_paths(path: Path):
    base_dir = get_table_dir(path)

    return TablePaths(
        music=base_dir / 'mmMusic.bin',
        score=base_dir / 'mmScore.bin',
        fes_list=base_dir / 'mmFesList.bin',
        textout_ex=base_dir / 'mmtextout_ex.bin',
        textout_jp=base_dir / 'mmtextout_jp.bin',
    )


def get_cover_art_dirs(path: Path):
    base_sprite_dir = path / 'data' / 'sprite'

    return CoverArtPaths(
        full_size=base_sprite_dir / 'movie_selector',
        mirror_effect=base_sprite_dir / 'movie_thumbnail',
        small=base_sprite_dir / 'movie_selector_mini',
    )


def get_cover_art_paths_for_song(song: Song, base_dir: Path):
    base_dirs = get_cover_art_dirs(base_dir)

    for dir in base_dirs:
        dir.mkdir(parents=True, exist_ok=True)

    unquoted_name = DoubleQuotedString.remove_quotes(song.filename)

    return CoverArtPaths(
        full_size=base_dirs.full_size / f'{song.id:03}_mms_{unquoted_name}.dds',
        mirror_effect=base_dirs.mirror_effect / f'{song.id:03}_mmt_{unquoted_name}.dds',
        small=base_dirs.small / f'{song.id:03}_mms_{unquoted_name}.dds',
    )


def get_local_cover_art_paths_for_song(song: Song):
    return CoverArtPaths(
        full_size=Path.joinpath(song.full_size),
    )


def get_external_bg_video_path_for_song(song: Song, base_dir: Path):
    video_dir = base_dir / 'data' / 'movie'

    return video_dir / f'{song.id:03}_mmv_{DoubleQuotedString.remove_quotes(song.filename)}.wmv'


def get_external_soundbgm_path(base_dir: Path):
    return base_dir / 'data' / 'SoundBGM.txt'


def get_external_chart_path(chart: Chart, base_dir: Path, song_id_padding_length: int = 3) -> Path:
    """
    Gets the path in the Maimai FiNALE file tree based on the intended chart the file is intended to be used for.

    :param chart: The chart to get the file path for.
    :param base_dir: The base directory for the file tree. This is expected to be within the root folder of
    the file tree *(at the level including the executable for the game)*.
    :param song_id_padding_length: The number of digits used to 0-pad the song ID. On a vanilla install,
    this will always be 3 digits (the function's default value).
    :return: The path that the respective chart's file should be located within the game install.
    """
    unquoted_name = DoubleQuotedString.remove_quotes(chart.chart_song.filename)
    return (base_dir / 'data' / 'score' /
            # Allow for adjustable 0-padding length
            (f'{chart.song_id:0{song_id_padding_length}}_'
             f'{unquoted_name}_'
             f'{chart.difficulty_level_id:02}'
             f'.sdb'))
