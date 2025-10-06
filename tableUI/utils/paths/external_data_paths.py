from pathlib import Path
from typing import NamedTuple

from tableUI.db.models import Song
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
