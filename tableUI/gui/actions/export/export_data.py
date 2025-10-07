import datetime
import shutil
from pathlib import Path

from PySide6.QtWidgets import QWidget, QMessageBox
from sqlmodel import Session, select

from tableUI.const import BACKUP_PATH
from tableUI.db.models import Song
from tableUI.db.to_tables import get_all_tables
from tableUI.gui.actions.backup.backup_game_data import backup_game_data
from tableUI.parsers.tables.table_types.sound_bgm.table import write_session_soundbgm_to_path
from tableUI.utils.crypt.finale import encrypt_table_with_env_key
from tableUI.utils.paths.external_data_paths import get_encrypted_table_paths, get_cover_art_paths_for_song, \
    get_external_bg_video_path_for_song, get_external_soundbgm_path
from tableUI.utils.paths.internal_data_paths import get_internal_cover_art_paths_for_song_id, \
    get_internal_bg_video_path_for_song_id


def export_data(session: Session, game_dir: Path, parent: QWidget = None):
    try:
        backup_dir = BACKUP_PATH / datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        print(backup_dir)
        backup_game_data(game_dir, backup_dir, session)

        table_contents = get_all_tables(session)

        table_paths = get_encrypted_table_paths(game_dir)

        table_paths.music.parent.mkdir(parents=True, exist_ok=True)

        # Data Tables
        for plain_content, dest_path in (
                (table_contents.music, table_paths.music),
                (table_contents.score, table_paths.score),
                (table_contents.feslist, table_paths.fes_list),
                (table_contents.textouts.ex, table_paths.textout_ex),
                (table_contents.textouts.jp, table_paths.textout_jp)):

            # Ensure encoding is always little-endian for compatibility with host machines
            final_content = encrypt_table_with_env_key(bytes(plain_content.build_table(), encoding='utf-16-le'))

            with open(dest_path, "wb") as f:
                f.write(final_content)

        # SoundBGM
        soundbgm_path = get_external_soundbgm_path(game_dir)
        write_session_soundbgm_to_path(session, soundbgm_path)

        # Song Data
        songs_to_export = session.exec(select(Song).where(Song.is_vanilla == False)).all()

        for song in songs_to_export:
            # Song Covers
            cover_out_paths = get_cover_art_paths_for_song(song, game_dir)

            base_src_cover_art_path = get_internal_cover_art_paths_for_song_id(song.id)

            if (src_full_path := (base_src_cover_art_path / 'full.dds')).exists():
                shutil.copy2(src_full_path, cover_out_paths.full_size)
            #     print(cover_out_paths.full_size)
            # else:
            #     print(src_full_path)
            if (src_mirror_path := (base_src_cover_art_path / 'mirror.dds')).exists():
                shutil.copy2(src_mirror_path, cover_out_paths.mirror_effect)
            if (src_small_path := (base_src_cover_art_path / 'small.dds')).exists():
                shutil.copy2(src_small_path, cover_out_paths.small)

            # Song BG video
            bg_video_path = get_internal_bg_video_path_for_song_id(song_id=song.id)
            if bg_video_path.exists():
                shutil.copy2(
                    bg_video_path,
                    get_external_bg_video_path_for_song(song, game_dir)
                )

        QMessageBox.information(parent, 'Export successful', 'All data has been successfully exported.')

    except Exception as e:
        # raise e
        QMessageBox.critical(parent,
                             'Error Exporting Data',
                             f'An error occured when exporting data. ({type(e)}: {e})')

        # print(plain_content, dest_path)
