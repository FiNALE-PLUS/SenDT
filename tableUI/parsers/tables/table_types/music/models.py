from pydantic import Field, AliasChoices

from tableUI.parsers.tables.field_types.quoted_string import DoubleQuotedString
from tableUI.parsers.tables.table_types.abstract.row import TableRow
from tableUI.parsers.tables.table_types.abstract.table import TableWithUnparsedHeader
from tableUI.parsers.tables.table_types.fes_list.head_string import FESLIST_HEAD_STRING
from tableUI.parsers.tables.table_types.music.head_string import SONGLIST_HEAD_STRING


# TODO
class MusicRow(TableRow):
    id: int = Field(validation_alias=AliasChoices('id', 'ID'))
    name_id: str = Field(validation_alias=AliasChoices('name_id', 'NAME'),
                         pattern=r'^eMusic_\d{3}$')
    version: int = Field(validation_alias=AliasChoices('version', 'Ver'))
    subcategory: int = Field(validation_alias=AliasChoices('subcategory', 'SubCate'))
    bpm: float = Field(validation_alias=AliasChoices('bpm', 'BPM'), gt=0)
    sort_id: int = Field(validation_alias=AliasChoices('sort_id', 'SortID'))
    dress: bool = Field(validation_alias=AliasChoices('dress', 'ドレス'))
    darkness: bool = Field(validation_alias=AliasChoices('darkness', '暗黒'))
    miles_counted: bool = Field(validation_alias=AliasChoices('miles_counted', 'mile'))
    vl: bool = Field(validation_alias=AliasChoices('vl', 'VL'))
    event_id: int = Field(validation_alias=AliasChoices('event_id', 'Event'))
    play_recording_enabled: bool = Field(validation_alias=AliasChoices('play_recording_enabled', 'Rec'))
    preview_start_time: float = Field(validation_alias=AliasChoices('preview_start_time', 'PVStart'))
    preview_end_time: float = Field(validation_alias=AliasChoices('preview_end_time', 'PVEnd'))
    # 0 Represents no override
    song_length_override: int = Field(validation_alias=AliasChoices('song_length_override', '曲長さ'),
                                      default=0)
    off_ranking: int = Field(validation_alias=AliasChoices('off_ranking', 'オフRanking'))
    ad_def: int = Field(validation_alias=AliasChoices('ad_def', 'AD Def'))
    re_master: int = Field(validation_alias=AliasChoices('re_master', 'ReMaster'))
    special_pv: bool = Field(validation_alias=AliasChoices('special_pv', '特殊PV'))
    # Unused - no assumptions made about data type
    challenge_track: int = Field(validation_alias=AliasChoices('challenge_track', 'チャレンジトラック'))
    bonus: int = Field(validation_alias=AliasChoices('bonus', 'ボーナス'))
    genre_id: int = Field(validation_alias=AliasChoices('genre_id', 'GenreID'))
    textout_title_id: str = Field(validation_alias=AliasChoices('textout_title_id', 'タイトル'))
    textout_artist_id: str = Field(validation_alias=AliasChoices('textout_artist_id', 'アーティスト'))
    sort_id_jp: int = Field(validation_alias=AliasChoices('sort_id_jp', 'sort_jp_index'))
    sort_id_en: int = Field(validation_alias=AliasChoices('sort_id_en', 'sort_ex_index'))
    base_file_name: DoubleQuotedString = Field(validation_alias=AliasChoices('base_file_name', 'filename'),
                                               pattern=r'^"[a-z0-9_]+"$')


class MusicTable(TableWithUnparsedHeader):
    _head = SONGLIST_HEAD_STRING

    _internal_table_name = 'MMMUSIC'
    _include_trailing_comma = False

    def __init__(self, rows: list[MusicRow] = None):
        super().__init__(rows)

    def sort_rows(self):
        self._rows = sorted(self.rows, key=lambda r: r.id)
