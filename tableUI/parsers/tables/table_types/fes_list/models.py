from pydantic import Field, AliasChoices

from tableUI.parsers.tables.table_types.abstract.row import TableRow
from tableUI.parsers.tables.table_types.abstract.table import TableWithUnparsedHeader
from tableUI.parsers.tables.table_types.fes_list.head_string import FESLIST_HEAD_STRING


class FesListRow(TableRow):
    name: str = Field(validation_alias=AliasChoices('name', 'NAME'),
                      pattern=r'^eFesList_\d{4}$')
    id: int = Field(validation_alias=AliasChoices('id', 'ID'))
    event_id: int = Field(validation_alias=AliasChoices('event_id', 'EVENT'))
    sort_id: int = Field(validation_alias=AliasChoices('sort_id', 'SordID'))
    score_id: int = Field(validation_alias=AliasChoices('score_id', 'ScoreID'))
    utage_difficulty_id: int = Field(validation_alias=AliasChoices('utage_difficulty_id', 'Dif'))
    chart_creator_id: int = Field(validation_alias=AliasChoices('chart_creator_id', 'Creator'),
                                  default=0)
    mirror: int = Field(validation_alias=AliasChoices('mirror', 'Mirror'))
    display: int = Field(validation_alias=AliasChoices('display', 'Disp'))
    skip: int = Field(validation_alias=AliasChoices('skip', 'Skip'))
    judge: int = Field(validation_alias=AliasChoices('judge', 'Judge'))
    rst_comment_id: str = Field(validation_alias=AliasChoices('rst_comment_id', 'RstCommentID'),
                                pattern=r'^RST_FES_COM_\d{4}$')


class FesListTable(TableWithUnparsedHeader):
    _head = FESLIST_HEAD_STRING

    _internal_table_name = 'MMFESLIST'
    _include_trailing_comma = True

    def __init__(self, rows: list[FesListRow] = None):
        super().__init__(rows)

    def sort_rows(self):
        self._rows = sorted(self.rows, key=lambda r: r.id)
