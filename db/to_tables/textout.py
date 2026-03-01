from typing import NamedTuple

from sqlmodel import Session, select

from db.models import ChartCreator, Song
from tableUI.parsers.tables.field_types.quoted_string import TextoutQuotedString
from tableUI.parsers.tables.textout.models import FilledMusicTextoutExTable, FilledMusicTextoutJpTable, TextoutRow


class TextoutLangsTuple(NamedTuple):
    ex: FilledMusicTextoutExTable
    jp: FilledMusicTextoutJpTable


def build_music_textout_tables_from_db(session: Session) -> TextoutLangsTuple:
    ex_table = FilledMusicTextoutExTable()
    jp_table = FilledMusicTextoutJpTable()

    add_chart_creators_to_textouts(session, ex_table, jp_table)
    add_chart_song_data_to_textouts(session, ex_table, jp_table)

    return TextoutLangsTuple(
        ex=ex_table,
        jp=jp_table,
    )


def add_chart_creators_to_textouts(session: Session,
                                   ex_table: FilledMusicTextoutExTable, jp_table: FilledMusicTextoutJpTable):
    chart_creators = session.exec(select(ChartCreator)).fetchall()

    ex_table.add_rows(*[TextoutRow(
        text_id=TextoutQuotedString(f"RST_SCORECREATOR_{creator.id:04}"),
        text_value=TextoutQuotedString(creator.name_en)
    )
        for creator in chart_creators])

    jp_table.add_rows(*[TextoutRow(
        text_id=TextoutQuotedString(f"RST_SCORECREATOR_{creator.id:04}"),
        text_value=TextoutQuotedString(creator.name_jp)
    )
        for creator in chart_creators])


def add_chart_song_data_to_textouts(session: Session,
                                    ex_table: FilledMusicTextoutExTable, jp_table: FilledMusicTextoutJpTable):
    song_data = session.exec(select(Song)).fetchall()

    for song in song_data:
        ex_table.add_rows(
            TextoutRow(text_id=TextoutQuotedString(f'RST_MUSICARTIST_{song.id:04}'),
                       text_value=TextoutQuotedString(song.artist.name_en)),
            TextoutRow(text_id=TextoutQuotedString(f'RST_MUSICTITLE_{song.id:04}'),
                       text_value=TextoutQuotedString(song.name_en)),
        )
        jp_table.add_rows(
            TextoutRow(text_id=TextoutQuotedString(f'RST_MUSICARTIST_{song.id:04}'),
                       text_value=TextoutQuotedString(song.artist.name_jp)),
            TextoutRow(text_id=TextoutQuotedString(f'RST_MUSICTITLE_{song.id:04}'),
                       text_value=TextoutQuotedString(song.name_jp)),
        )

    # print(song_data[0])
    # print(song_data[0].artist)
