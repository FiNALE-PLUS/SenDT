import re
from pathlib import Path

from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from tableUI.db.fill_db.validation import validate_textout_table_lengths_equal, validate_row_ids_at_same_index, \
    validate_generic_table_lengths_equal, validate_generic_ids_match
from tableUI.db.models import SongArtist, ChartCreator, Song, SongGenre, UtageEntry, Chart
from tableUI.parsers.parse import parse_plain_textout, parse_music_table, parse_score_table, parse_fes_list_table
from tableUI.parsers.tables.field_types.quoted_string import DoubleQuotedString
from tableUI.parsers.tables.table_types.fes_list.models import FesListRow
from tableUI.parsers.tables.table_types.music.models import MusicTable
from tableUI.parsers.tables.textout.models import FilledMusicTextoutExTable, TextoutRow, column_name_patterns, \
    FilledMusicTextoutJpTable

score_name_pattern = re.compile(r"eScore_(?P<padded_song_id>\d{3})_(?P<safename>[a-z0-9_]+)_(?P<padded_difficulty_id>\d{2})")


def fill_db_from_table_files(session: Session,
                             music_path: Path, score_path: Path, feslist_path: Path,
                             textout_ex_path: Path, textout_jp_path: Path,
                             vanilla_tables: bool = False,):
    fill_chart_creators_from_textout_files(session, textout_ex_path, textout_jp_path)
    fill_artists_from_textout_files(session, textout_ex_path, textout_jp_path)

    fill_songs_from_table_files(session, music_path, textout_ex_path, textout_jp_path, vanilla_tables=vanilla_tables)

    fill_charts_from_table_files(session, score_path, feslist_path)


def get_artists_from_textout_tables(textout_ex_path: Path, textout_jp_path: Path):
    ex_artist_tbl = FilledMusicTextoutExTable(
        parse_plain_textout(textout_ex_path,
                            'MMTEXTOUT', TextoutRow, key_filter_pattern=column_name_patterns['artist']))
    jp_artist_tbl = FilledMusicTextoutJpTable(
        parse_plain_textout(textout_jp_path,
                            'MMTEXTOUT', TextoutRow, key_filter_pattern=column_name_patterns['artist']))

    return ex_artist_tbl, jp_artist_tbl


def get_song_names_from_textout_tables(textout_ex_path: Path, textout_jp_path: Path):
    ex_title_tbl = FilledMusicTextoutExTable(
        parse_plain_textout(textout_ex_path,
                            'MMTEXTOUT', TextoutRow, key_filter_pattern=column_name_patterns['title']))
    jp_title_tbl = FilledMusicTextoutJpTable(
        parse_plain_textout(textout_jp_path,
                            'MMTEXTOUT', TextoutRow, key_filter_pattern=column_name_patterns['title']))

    return ex_title_tbl, jp_title_tbl


def fill_chart_creators_from_textout_files(session: Session, textout_ex_path: Path, textout_jp_path: Path,
                                           overwrite: bool = False) -> int:
    ex_creator_tbl = FilledMusicTextoutExTable(
        parse_plain_textout(textout_ex_path,
                            'MMTEXTOUT', TextoutRow, key_filter_pattern=column_name_patterns['chart_creator']))
    jp_creator_tbl = FilledMusicTextoutJpTable(
        parse_plain_textout(textout_jp_path,
                            'MMTEXTOUT', TextoutRow, key_filter_pattern=column_name_patterns['chart_creator']))

    validate_textout_table_lengths_equal(ex_creator_tbl, jp_creator_tbl, 'chart creator')

    rows_modified = 0
    for idx in range(len(ex_creator_tbl.rows)):
        validate_row_ids_at_same_index(ex_creator_tbl.rows[idx], jp_creator_tbl.rows[idx], row_type='chart creator')

        creator_id = column_name_patterns['chart_creator'].search(ex_creator_tbl.rows[idx].text_id).group(
            'chart_creator_id')

        tbl_creator = ChartCreator(
            id=creator_id,
            name_en=ex_creator_tbl.rows[idx].text_value,
            name_jp=jp_creator_tbl.rows[idx].text_value,
        )

        try:
            db_creator = session.exec(select(ChartCreator).where(ChartCreator.id == tbl_creator.id)).one()
            if overwrite:
                db_creator.name_en = tbl_creator.name_en
                db_creator.name_jp = tbl_creator.name_jp

                session.add(db_creator)
                rows_modified += 1

        except NoResultFound:
            session.add(tbl_creator)
            rows_modified += 1

    return rows_modified


# TODO: Add overwrite
def fill_artists_from_textout_files(session: Session, textout_ex_path: Path, textout_jp_path: Path) -> int:
    """
    Inserts any artists from textout tables which are not identical to any existing artists.
    Requires that all rows are correctly sorted and of the same length.
    :param session:
    :param textout_ex_path:
    :param textout_jp_path:
    :return:
    """
    ex_artist_tbl, jp_artist_tbl = get_artists_from_textout_tables(textout_ex_path, textout_jp_path)

    validate_textout_table_lengths_equal(ex_artist_tbl, jp_artist_tbl, 'artist')

    rows_modified = 0
    for idx in range(len(ex_artist_tbl.rows)):
        validate_row_ids_at_same_index(ex_artist_tbl.rows[idx], jp_artist_tbl.rows[idx], row_type='artist')

        tbl_artist = SongArtist(name_en=ex_artist_tbl.rows[idx].text_value, name_jp=jp_artist_tbl.rows[idx].text_value)

        try:
            session.exec(select(SongArtist).
                         where(SongArtist.name_en == tbl_artist.name_en).
                         where(SongArtist.name_jp == tbl_artist.name_jp)).one()

        except NoResultFound:
            session.add(
                tbl_artist
            )
            rows_modified += 1

    return rows_modified


def fill_songs_from_table_files(session: Session, music_path: Path, textout_ex_path: Path, textout_jp_path: Path,
                                vanilla_tables: bool = False):
    music_tbl = parse_music_table(music_path)

    ex_artist_tbl, jp_artist_tbl = get_artists_from_textout_tables(textout_ex_path, textout_jp_path)
    ex_title_tbl, jp_title_tbl = get_song_names_from_textout_tables(textout_ex_path, textout_jp_path)

    validate_generic_table_lengths_equal(music_tbl,
                                         ex_artist_tbl, jp_artist_tbl,
                                         ex_title_tbl, jp_title_tbl)

    for idx in range(len(music_tbl)):
        music_row = music_tbl.rows[idx]

        ex_artist_id = int(
            column_name_patterns['artist'].search(ex_artist_tbl.rows[idx].text_id).group('song_artist_id'))
        jp_artist_id = int(
            column_name_patterns['artist'].search(jp_artist_tbl.rows[idx].text_id).group('song_artist_id'))
        ex_title_id = int(
            column_name_patterns['title'].search(ex_title_tbl.rows[idx].text_id).group('song_id')
        )
        jp_title_id = int(
            column_name_patterns['title'].search(jp_title_tbl.rows[idx].text_id).group('song_id')
        )

        validate_generic_ids_match(music_row.id, ex_artist_id, jp_artist_id, ex_title_id, jp_title_id)

        # print(music_row)
        song_artist = session.exec(select(SongArtist).
                                where(SongArtist.name_en == ex_artist_tbl.rows[idx].text_value).
                                where(SongArtist.name_jp == jp_artist_tbl.rows[idx].text_value)).one()
        song_name_ex = ex_title_tbl.rows[idx].text_value
        song_name_jp = jp_title_tbl.rows[idx].text_value

        try:
            existing_song = session.exec(select(Song).where(Song.id == music_row.id)).one()

        except NoResultFound:
            tbl_song = Song(
                id=music_row.id,
                is_vanilla=vanilla_tables,
                artist=song_artist,
                genre=session.exec(select(SongGenre).where(SongGenre.id == music_row.genre_id)).one(),
                name_en=song_name_ex,
                name_jp=song_name_jp,
                version=music_row.version,
                sub_category=music_row.subcategory,
                bpm=music_row.bpm,
                sort_id=music_row.sort_id,
                dress=music_row.dress,
                darkness=music_row.darkness,
                miles_counted=music_row.miles_counted,
                vl=music_row.vl,
                event_id=music_row.event_id,
                play_recording_enabled=music_row.play_recording_enabled,
                preview_start_time=music_row.preview_start_time,
                preview_end_time=music_row.preview_end_time,
                song_length_override=music_row.song_length_override,
                off_ranking=music_row.off_ranking,
                ad_def=music_row.ad_def,
                re_master=music_row.re_master,
                special_pv=music_row.special_pv,
                challenge_track=music_row.challenge_track,
                bonus=music_row.bonus,
                sort_jp_index=music_row.sort_id_jp,
                sort_ex_index=music_row.sort_id_en,
                filename=music_row.base_file_name,
            )
            session.add(tbl_song)

    session.commit()


def fill_charts_from_table_files(session: Session, score_path: Path, feslist_path: Path):
    chart_tbl = parse_score_table(score_path)

    feslist_tbl = parse_fes_list_table(feslist_path)

    unlinked_charts = 0

    for row in chart_tbl:
        name_match = score_name_pattern.search(row.name)
        if name_match is None:
            raise ValueError(f"Invalid chart name {row.name}")

        chart_song_id = int(name_match.group("padded_song_id"))
        chart_safename = DoubleQuotedString(name_match.group("safename"))
        chart_difficulty_level_id = int(name_match.group("padded_difficulty_id"))

        expected_chart_id = f'{chart_song_id}{name_match.group("padded_difficulty_id")}'
        if str(row.id) != expected_chart_id:
            raise ValueError(f"Invalid chart id {row.id} (Expected: {expected_chart_id})")

        utage_row: FesListRow | None = None
        utage_model: UtageEntry | None = None
        for feslist_row in feslist_tbl:
            if feslist_row.score_id == row.id:
                utage_row = feslist_row
                # print("match")
                break
            # else:
            #     print(feslist_row.score_id, row.id)

        # Add base chart row if necessary
        added_chart = False
        try:
            chart_song = session.exec(select(Song).where(Song.filename == chart_safename)).one()
            existing_chart = session.exec(select(Chart).
                                          where(Chart.chart_song == chart_song).
                                          where(Chart.difficulty_level_id == chart_difficulty_level_id)).one()

        # Only add the chart if one does not exist at its ID and the song already exists
        except NoResultFound:
            try:
                session.exec(select(Song).where(Song.id == chart_song_id)).one()

                chart_model = Chart(
                    # id=row.id,
                    song_id=chart_song_id,
                    difficulty_constant=row.chart_difficulty_constant,
                    difficulty_level_id=chart_difficulty_level_id,
                    affects_rating=row.affects_rating,
                    creator_id=row.chart_creator_id,
                )

                session.add(chart_model)
                added_chart = True

            except NoResultFound:
                unlinked_charts += 1
        # Add utage chart row if none is found for the specified chart ID
        if utage_row is not None and added_chart:
            # print(utage_row)
            try:
                existing_utage_chart = session.exec(select(UtageEntry).
                                                    where(UtageEntry.chart_id == row.id).
                                                    where(UtageEntry.utage_type_id == utage_row.utage_difficulty_id)
                                                    ).one()

            except NoResultFound:
                utage_model = UtageEntry(
                    id=utage_row.id,
                    # Either Chart ID would suffice (as they should be identical), this is chosen by preference
                    chart_id=chart_model.id,
                    sort_id=utage_row.sort_id,
                    event_id=utage_row.event_id,
                    utage_type_id=utage_row.utage_difficulty_id,
                    mirror=utage_row.mirror,
                    display=utage_row.display,
                    skip=utage_row.skip,
                    judge=utage_row.judge,
                )

                session.add(utage_model)

    session.commit()

    return unlinked_charts
    # print(chart_tbl.rows[0])

