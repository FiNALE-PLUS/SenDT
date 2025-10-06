import datetime
import shutil
from pathlib import Path

from PySide6.QtWidgets import QWidget, QMessageBox
from sqlmodel import Session, select

from tableUI.const import BACKUP_PATH
from tableUI.db.models import Song
from tableUI.db.to_tables import get_all_tables
from tableUI.gui.actions.backup.backup_game_data import backup_game_data
from tableUI.utils.crypt.finale import encrypt_table_with_env_key
from tableUI.utils.paths.external_data_paths import get_encrypted_table_paths, get_cover_art_paths_for_song
from tableUI.utils.paths.internal_data_paths import get_internal_cover_art_paths_for_song_id


def export_data(session: Session, game_dir: Path, parent: QWidget = None):
    try:
        backup_dir = BACKUP_PATH / datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_game_data(game_dir, backup_dir, session)

        table_contents = get_all_tables(session)

        table_paths = get_encrypted_table_paths(game_dir)

        table_paths.music.parent.mkdir(parents=True, exist_ok=True)

        for plain_content, dest_path in (
                (table_contents.music, table_paths.music),
                (table_contents.score, table_paths.score),
                (table_contents.feslist, table_paths.fes_list),
                (table_contents.textouts.ex, table_paths.textout_ex),
                (table_contents.textouts.jp, table_paths.textout_jp)):

            final_content = encrypt_table_with_env_key(bytes(plain_content.build_table(), encoding='utf-16'))

            # bytes(chart_string, encoding="ascii")

            with open(dest_path, "wb") as f:
                f.write(final_content)

        songs_to_export = session.exec(select(Song).where(Song.is_vanilla == False)).all()

        # print(songs_to_export)

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

        QMessageBox.information(parent, 'Export successful', 'All data has been successfully exported.')

    except Exception as e:
        raise e
        QMessageBox.critical(parent,
                             'Error Exporting Data',
                             f'An error occured when exporting data. ({type(e)}: {e})')

        # print(plain_content, dest_path)
