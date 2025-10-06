from collections import namedtuple
from typing import TypedDict, NamedTuple

from sqlmodel import Session

from tableUI.db.to_tables.feslist import build_feslist_table_from_db
from tableUI.db.to_tables.music import build_music_table_from_db
from tableUI.db.to_tables.score import build_score_table_from_db
from tableUI.db.to_tables.textout import build_music_textout_tables_from_db, TextoutLangsTuple
from tableUI.parsers.tables.table_types.fes_list.models import FesListTable
from tableUI.parsers.tables.table_types.music.models import MusicTable
from tableUI.parsers.tables.table_types.score.models import ScoreTable
from tableUI.parsers.tables.textout.models import FilledMusicTextoutExTable, FilledMusicTextoutJpTable


class FullTableSet(NamedTuple):
    textouts: TextoutLangsTuple
    feslist: FesListTable
    music: MusicTable
    score: ScoreTable


def get_all_tables(session: Session):
    return FullTableSet(
        textouts=build_music_textout_tables_from_db(session),
        feslist=build_feslist_table_from_db(session, use_english_song_names=True),
        music=build_music_table_from_db(session),
        score=build_score_table_from_db(session)
    )
