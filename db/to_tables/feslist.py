from sqlmodel import Session, select

from db.models import UtageEntry
from tableUI.parsers.tables.field_types.quoted_string import TextoutQuotedString
from tableUI.parsers.tables.table_types.fes_list.models import FesListTable, FesListRow


def build_feslist_table_from_db(session: Session, use_english_song_names: bool = True) -> FesListTable:
    feslist_tbl = FesListTable()

    utage_entries = session.exec(select(UtageEntry).order_by(UtageEntry.id)).fetchall()

    feslist_tbl.add_rows(
        *[FesListRow(
            name=f'eFesList_{entry.id:04}',
            id=entry.id,
            event_id=entry.event_id,
            sort_id=entry.sort_id,
            score_id=int(f'{entry.utage_chart.chart_song.id}{entry.utage_chart.difficulty_level_id:02}'),
            utage_difficulty_id=entry.utage_type_id,
            # In vanilla tables, ths column is unused
            # TODO: Investigate whether this column can be used to display creators in utages,
            #  or if this is unecessary and they are taken from mmScore
            chart_creator_id=0,
            mirror=entry.mirror,
            display=entry.display,
            skip=entry.skip,
            judge=entry.judge,
            rst_comment_id=f'RST_FES_COM_{entry.id:04}',
            # TODO: Replace slicing with a less brittle solution
            #  (would not remove quoted strings that do not use textout quotes)
            comment=f'[{entry.utage_entry_type.kanji}] '
                    f'( '
                    f'{TextoutQuotedString.remove_quotes(entry.utage_chart.chart_song.name_en)
                    if use_english_song_names 
                    else TextoutQuotedString.remove_quotes(entry.utage_chart.chart_song.name_jp)}'
                    f' )'
        ) for entry in utage_entries]
    )

    return feslist_tbl
