from decimal import Decimal
from typing import Optional

from pydantic import Field, AliasChoices

from tableUI.parsers.tables.field_types.quoted_string import DoubleQuotedString
from tableUI.parsers.tables.table_types.abstract.row import TableRow
from tableUI.parsers.tables.table_types.abstract.table import TableWithUnparsedHeader
from tableUI.parsers.tables.table_types.score.head_string import SCORE_LIST_HEAD_STRING


class ScoreRow(TableRow):
    id: int = Field(validation_alias=AliasChoices('id', 'ID'))
    name: str = Field(validation_alias=AliasChoices('name', 'NAME'),
                      pattern=r'^eScore_\d{3}_[0-9a-z_]+_\d{2}$')
    chart_difficulty_constant: Decimal = Field(validation_alias=AliasChoices('chart_difficulty_constant', 'LV'),
                                               decimal_places=1, le=14, ge=0)
    chart_creator_id: int = Field(validation_alias=AliasChoices('chart_creator_id', '譜面作者ID'))
    affects_rating: bool = Field(validation_alias=AliasChoices('affects_rating', '計算対象'))
    internal_chart_name: DoubleQuotedString = Field(validation_alias=AliasChoices('internal_chart_name', 'safename'),
                                                    pattern=r'^"\d{3}_[0-9a-z_]+_\d{2}"$'
                                                    )


class ScoreTable(TableWithUnparsedHeader):
    _head = SCORE_LIST_HEAD_STRING

    _internal_table_name = 'MMSCORE'
    _include_trailing_comma = False

    def __init__(self, rows: list[ScoreRow] = None):
        super().__init__(rows)

    def sort_rows(self):
        self._rows = sorted(self.rows, key=lambda r: r.id)
