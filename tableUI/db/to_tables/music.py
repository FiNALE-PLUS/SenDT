from sqlmodel import Session, select

from tableUI.db.models import Song
from tableUI.parsers.tables.field_types.quoted_string import DoubleQuotedString
from tableUI.parsers.tables.table_types.music.models import MusicTable, MusicRow


def build_music_table_from_db(session: Session) -> MusicTable:
    music_db_rows = session.exec(
        select(Song).order_by(Song.id)
    ).fetchall()

    music_tbl = MusicTable([
        MusicRow(
            id=song.id,
            name_id=f'eMusic_{song.id:03}',
            version=song.version,
            subcategory=song.sub_category,
            bpm=song.bpm,
            sort_id=song.sort_id,
            dress=song.dress,
            darkness=song.darkness,
            miles_counted=song.miles_counted,
            vl=song.vl,
            event_id=song.event_id,
            play_recording_enabled=song.play_recording_enabled,
            preview_start_time=song.preview_start_time,
            preview_end_time=song.preview_end_time,
            song_length_override=song.song_length_override,
            off_ranking=song.off_ranking,
            ad_def=song.ad_def,
            re_master=song.re_master,
            special_pv=song.special_pv,
            challenge_track=song.challenge_track,
            bonus=song.bonus,
            genre_id=song.genre_id,
            textout_artist_id=f'RST_MUSICARTIST_{song.id:04}',
            textout_title_id=f'RST_MUSICTITLE_{song.id:04}',
            sort_id_jp=song.sort_jp_index,
            sort_id_en=song.sort_ex_index,
            base_file_name=DoubleQuotedString(song.filename)
        ) for song in music_db_rows
    ])

    return music_tbl
