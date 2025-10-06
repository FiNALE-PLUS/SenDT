import datetime
import re
from io import TextIOWrapper
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from tableUI.parsers.tables.table_types.fes_list.models import FesListRow, FesListTable
from tableUI.parsers.tables.table_types.music.models import MusicRow, MusicTable
from tableUI.parsers.tables.table_types.score.models import ScoreTable, ScoreRow
from tableUI.parsers.tables.textout.models import TextoutRow

table_definition_pattern = re.compile(r"^#define (?P<internal_table_name>[A-Z_]+)$")
table_comment_pattern = re.compile(r'^/// @(?P<key>\w+) +(?P<value>.+)$')


class TableHeader(BaseModel):
    file: str = Field(pattern=r"^mm\w+.tbl$")
    file_brief: str
    author: str
    date: datetime.datetime
    note: str

    arbitrary_code_definitions: str

    table_brief: str
    columns: list[str]

    foot: list[str] | None = None

def get_table_encoding(path: Path):
    with open(path, 'rb') as f:
        if f.read(2) == b'\xff\xfe':
            return 'utf-16'
    return 'utf-8'

# TODO: Get text_table_ex name and extra fields (or parse into typed fields)
def parse_plain_table_header(table_file: TextIOWrapper) -> TableHeader:
    table_file.seek(0)

    header_fields = {}

    last_line_point = 0

    # 1st comment block
    while (line := table_file.readline()).startswith('///'):
        last_line_point = table_file.tell()
        if comment_match := table_comment_pattern.match(line):
            # print(comment_match)
            if comment_match.group('key') in ('file', 'brief', 'author', 'date', 'note'):
                # Convert file timestamp to a datetime
                if comment_match.group('key') == 'date':
                    header_fields['date'] = datetime.datetime.strptime(comment_match.group('value'), '%Y/%m/%d %H:%M:%S')
                # Differentiate between the two brief fields used
                # elif comment_match.group('key') == 'brief':
                #     if 'file_brief' not in header_fields:
                #         header_fields['file_brief'] = comment_match.group('value')
                #     else:
                #         header_fields['table_brief'] = comment_match.group('value')
                #         expected_column_definition = table_comment_pattern.match(table_file.readline())
                #         if expected_column_definition is None or expected_column_definition.group('key') != 'note':
                #             raise ValueError('Table column definition is not in the expected location (expected to be the line after text_table_ex name definition)')
                #
                #         print(expected_column_definition.group('value'))
                # All other fields do not need transformation
                else:
                    header_fields[comment_match.group('key')] = comment_match.group('value')

            else:
                raise ValueError(f'Unknown header comment key {comment_match.group("key")}')

    table_file.seek(last_line_point)

    table_name = ''

    arbitrary_code_definitions = ''
    while not (line := table_file.readline()).startswith('///'):
        last_line_point = table_file.tell()
        arbitrary_code_definitions += line
    header_fields['arbitrary_code_definitions'] = arbitrary_code_definitions


    table_file.seek(last_line_point)

    print(arbitrary_code_definitions)


    table_file.seek(0)

    return TableHeader(**header_fields)



def parse_plain_table_content(table_file: TextIOWrapper, row_model: type) -> list[BaseModel]:
    table_file.seek(0)

    table_name = ''

    while not table_name:
        line = table_file.readline()
        if tab_match := table_definition_pattern.match(line):
            table_name = tab_match.group('internal_table_name').split('_')[0]

    columns = []

    while not columns:
        line = table_file.readline()
        if line.startswith(f'/// @note {table_name}'):
            column_definitions = line[line.index('(') + 1 : line.index(')')].strip()
            columns = column_definitions.split(',')
            columns = [column.strip() for column in columns]
            # TODO: Validate text_rows_ex, accounting for trailing comma when found in definition

    values = []

    while line := table_file.readline():
        if line.startswith(table_name):

            # Get text_table_ex column values
            row_vals = line[line.index('(') + 1: line.index(')')].strip()
            vals = row_vals.split(',')
            # TODO: Validate trailing 'columns' when specified in text_table_ex note
            vals = [column.strip() for column in vals]

            non_empty_vals = [column for column in vals if column]
            row_dict = {
                k: v for k, v in zip(columns, non_empty_vals)
            }

            # Get row comment, if it exists
            commentsplit = line.strip().split('///<')
            match len(commentsplit):
                # case 1:
                #     row_dict['comment'] = None
                case 2:
                    row_dict['comment'] = commentsplit[-1].strip()
                case _:
                    raise ValueError(f'Table row seems to have more than one comment (found {len(commentsplit) - 1})')

            values.append(row_model(**row_dict))
            # print(non_empty_vals)

    return values

def parse_plain_table_file(path: Path, row_model: type) -> list[BaseModel]:
    with open(path, 'r', encoding=get_table_encoding(path)) as f:
        return parse_plain_table_content(f, row_model)


def parse_fes_list_table(path: Path) -> FesListTable:
    return FesListTable(parse_plain_table_file(path, FesListRow))


def parse_score_table(path: Path) -> ScoreTable:
    return ScoreTable(parse_plain_table_file(path, ScoreRow))


def parse_music_table(path: Path) -> MusicTable:
    return MusicTable(parse_plain_table_file(path, MusicRow))


# def parse_plain_music_table(out_path: Path) -> MusicTable:
#     with open(out_path, 'r', encoding=get_table_encoding(out_path)) as f:
#         return parse_music_table(f)


def parse_plain_textout(path: Path, internal_table_name: str, row_model: type[TextoutRow],
                        key_filter_pattern: Optional[re.Pattern] = None,
                        value_filter_pattern: Optional[re.Pattern] = None) -> list[TextoutRow]:
    rows: list[TextoutRow] = []

    # model_columns = {k: v for k, v in row_model.model_fields.items() if k != 'comment'}
    model_columns = [k for k in row_model.model_fields.keys() if k != 'comment']
    assert len(model_columns) == 2

    encoding = get_table_encoding(path)

    # Use a unicode pattern to ensure that all unicode characters can be correctly matched
    textout_column_content_pattern = re.compile(u'L\"(?P<content>[^\"]*)\"')

    with open(path, 'r', encoding=encoding) as textout_file:
        for line in textout_file:
            if line.startswith(internal_table_name):

                column_values = textout_column_content_pattern.findall(line)
                # print(column_values)
                # print(model_columns)

                assert len(column_values) == 2

                # Validate key and value against given patterns
                if key_filter_pattern is not None:
                    if not key_filter_pattern.match(column_values[0]):
                        continue
                if value_filter_pattern is not None:
                    if not value_filter_pattern.match(column_values[1]):
                        continue

                row_values = {}
                for idx, column in enumerate(model_columns):
                    row_values[column] = column_values[idx]

                row = row_model(**row_values)

                rows.append(row)

    return rows

#
# def parse_plain_table(out_path: Path):
#     ...