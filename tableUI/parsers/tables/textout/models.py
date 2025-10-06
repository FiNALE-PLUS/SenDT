import re
from abc import ABC
from typing import Optional, TypedDict

from pydantic import Field, AliasChoices

from tableUI.parsers.tables.field_types.quoted_string import DoubleQuotedString, TextoutQuotedString
from tableUI.parsers.tables.table_types.abstract.row import TableRow
from tableUI.parsers.tables.table_types.abstract.table import TableWithUnparsedHeader
from tableUI.parsers.tables.table_types.fes_list.head_string import FESLIST_HEAD_STRING
from tableUI.parsers.tables.textout.head_foot_ex import TEXTOUT_EX_HEAD_STRING, TEXTOUT_EX_CONTENT_HEAD, \
    TEXTOUT_EX_CONTENT_FOOT
from tableUI.parsers.tables.textout.head_foot_jp import TEXTOUT_JP_HEAD_STRING, TEXTOUT_JP_CONTENT_HEAD, \
    TEXTOUT_JP_CONTENT_FOOT

song_title_pattern = r'(?P<song_title>RST_MUSICTITLE_(?P<song_id>\d{4}))'
song_artist_pattern = r'(?P<song_artist>RST_MUSICARTIST_(?P<song_artist_id>\d{4}))'
chart_creator_pattern = r'(?P<chart_creator>RST_SCORECREATOR_(?P<chart_creator_id>\d{4}))'
safename_pattern = r'(?P<safename>[a-zA-Z-0-9]([a-zA-Z0-9_]*[a-zA-Z-0-9])|[a-zA-Z-0-9]*)'

class PatternDict(TypedDict):
    title: re.Pattern
    artist: re.Pattern
    chart_creator: re.Pattern
    safename: re.Pattern

column_name_patterns = PatternDict(
    title=re.compile(song_title_pattern),
    artist=re.compile(song_artist_pattern),
    chart_creator=re.compile(chart_creator_pattern),
    safename=re.compile(safename_pattern)
)

song_info_key_pattern = re.compile(song_title_pattern +
                                   r'|' + song_artist_pattern +
                                   r'|' + chart_creator_pattern)


def get_textout_music_row_sort_id(row: 'TextoutRow') -> int:
    """
    Returns an ID to sort music data text_rows_ex by, separating categories by using a multiple of 10000
    and using ID to sort within categories (since each category uses 4 digits for ID discrimination).

    :param row: the ``TextoutRow`` to get a sorting ID for
    :return: an ``int`` representing the sort ID of the row's ``text_id``
    """
    pattern_match = song_info_key_pattern.search(row.text_id)

    if pattern_match is None:
        raise ValueError(f"Row ID {row.text_id} does not contain music ID pattern: \n{song_info_key_pattern.pattern}")

    if pattern_match.group('song_artist_id') is not None:
        return 10000 + int(pattern_match.group('song_artist_id'))
    if pattern_match.group('song_id') is not None:
        return 20000 + int(pattern_match.group('song_id'))
    if pattern_match.group('chart_creator_id') is not None:
        return 30000 + int(pattern_match.group('chart_creator_id'))

    else:
        raise ValueError(f"Invalid music row ID {row.text_id} (This error should never happen - contact the developer)\n"
                         f"matches: {pattern_match.groupdict()}")




class TextoutRow(TableRow):
    text_id: TextoutQuotedString = Field(pattern=r'^L"[A-Za-z0-9_]+"$')
    text_value: TextoutQuotedString

    def get_table_column_values(self) -> list[str]:
        model_field_values = [getattr(self, field_name)
                              for field_name, field in self.__class__.model_fields.items()
                              if field_name != 'comment']

        return self.coerce_model_field_values(model_field_values)

    def get_plain_textout_table_row(self, table_name: str) -> str:
        table_column_values = self.get_table_column_values()

        return (
            f'{table_name}( {" ,".join(table_column_values)} )'
            f'{" ///< " + self.comment if self.comment is not None else ""}'
        )


# TODO: Add reading function for tables without a column header (check row width and fill from class field names?)
class UnfilledTextoutExTable(TableWithUnparsedHeader, ABC):
    """
    Represents an english textout text_table_ex with no content prefilled.
    """
    _head = TEXTOUT_EX_HEAD_STRING

    _internal_table_name = 'MMTEXTOUT'
    _include_trailing_comma = False
    _include_table_column_header = False

    def _get_stringified_content_row(self, row: TextoutRow, *column_widths: int) -> str:
        return row.get_plain_textout_table_row(self._internal_table_name)

    def __init__(self, rows: list[TextoutRow] = None):
        super().__init__(rows)


class FilledMusicTextoutExTable(UnfilledTextoutExTable):
    """
    Represents a English textout text_table_ex with all content filled outside of song names, artists and chart creators.
    """
    _head = TEXTOUT_EX_HEAD_STRING + '\n\n' + TEXTOUT_EX_CONTENT_HEAD
    _foot = TEXTOUT_EX_CONTENT_FOOT

    def sort_rows(self):
        self._rows = sorted(self.rows, key=lambda r: get_textout_music_row_sort_id(r))


class FilledMusicTextoutJpTable(FilledMusicTextoutExTable):
    """
    Represents a Japanese textout text_table_ex with all content filled outside of song names, artists and chart creators.
    """

    _head = TEXTOUT_JP_HEAD_STRING + '\n\n' + TEXTOUT_JP_CONTENT_HEAD
    _foot = TEXTOUT_JP_CONTENT_FOOT
