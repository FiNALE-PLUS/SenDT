import shutil
from pathlib import Path
from typing import NamedTuple

from sqlmodel import Session, select

from tableUI.db.models import Song
from tableUI.parsers.tables.field_types.quoted_string import DoubleQuotedString
from tableUI.utils.paths.external_data_paths import get_cover_art_paths_for_song, get_encrypted_table_paths, \
    get_table_dir, \
    get_chart_dir, get_external_soundbgm_path


class BackupDirs(NamedTuple):
    cover_art: Path


def get_backup_dirs(base_dir: Path) -> BackupDirs:
    return BackupDirs(
        cover_art=base_dir / 'cover_art',
    )


def backup_tables(in_path: Path, out_path: Path):
    get_table_dir(out_path).mkdir(parents=True, exist_ok=True)

    tables_in = get_encrypted_table_paths(in_path)
    tables_out = get_encrypted_table_paths(out_path)

    shutil.copy2(tables_in.music, tables_out.music)
    shutil.copy2(tables_in.score, tables_out.score)
    shutil.copy2(tables_in.fes_list, tables_out.fes_list)
    shutil.copy2(tables_in.textout_ex, tables_out.textout_ex)
    shutil.copy2(tables_in.textout_jp, tables_out.textout_jp)


def backup_soundbgm(in_path: Path, out_path: Path):

    backup_output_path = get_external_soundbgm_path(out_path)
    backup_output_path.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(get_external_soundbgm_path(in_path), out_path)


# TODO: Add backup and export of charts
def backup_charts(in_path: Path, out_path: Path):
    ...


def backup_game_data(in_path: Path, out_path: Path, session: Session) -> int:
    """
    Copies all data that could be overwritten by SenDT from ``in_path`` to ``out_path``.

    :param in_path: The source path to back up data from.
    :param out_path: The destination path to copy data to.
    :param session: A database session containing the current state of the songlist.
    :return: The number of songs backed up.
    """

    if not out_path.is_dir() and out_path.exists():
        raise ValueError('The given output path does not exist.')

    songs_to_backup = session.exec(select(Song).where(Song.is_vanilla == False)).all()

    if songs_to_backup:
        out_path.mkdir(parents=False, exist_ok=False)

        # Data table files and SoundBGM
        backup_tables(in_path, out_path)
        backup_soundbgm(in_path, out_path)

        chart_in_dir = get_chart_dir(in_path)
        chart_out_dir = get_chart_dir(out_path)

        # Backup song covers
        for song in songs_to_backup:

            # Cover Art
            source_cover_art_paths = get_cover_art_paths_for_song(song, in_path)
            backup_cover_art_paths = get_cover_art_paths_for_song(song, out_path)
            for source, dest in (
                    (source_cover_art_paths.full_size, backup_cover_art_paths.full_size),
                    (source_cover_art_paths.mirror_effect, backup_cover_art_paths.mirror_effect),
                    (source_cover_art_paths.small, backup_cover_art_paths.small)):
                try:
                    shutil.copy2(source, dest)
                except FileNotFoundError:
                    pass

            # Chart Files
            song_chart_files = chart_in_dir.glob(f'{song.id:03}_{DoubleQuotedString.remove_quotes(song.filename)}_??.s[rzcd]b')
            if song_chart_files:
                chart_out_dir.mkdir(parents=True, exist_ok=True)
            for file in song_chart_files:
                shutil.copy2(file, chart_out_dir / file.name)

    return len(songs_to_backup)

