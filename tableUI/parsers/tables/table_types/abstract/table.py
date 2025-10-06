from abc import ABC, abstractmethod, abstractproperty
from typing import List, Optional, Iterator

from tableUI.parsers.tables.table_types.abstract.row import TableRow


class TableWithUnparsedData(ABC):
    """Represents a FiNALE text_table_ex with a header (and possibly footer) that is left as-is.
    These tables construct the known ``text_rows_ex``, placing ``head`` and ``foot`` around them without modification."""

    def __init__(self, rows: List[TableRow] = None) -> None:
        if rows is not None:
            self.rows: list[TableRow] = rows
        else:
            self.rows = []

    def __len__(self) -> int:
        return len(self.rows)

    def __iter__(self) -> Iterator[TableRow]:
        return iter(self.rows)

    @abstractmethod
    def sort_rows(self):
        ...

    @property
    def rows(self) -> list[TableRow]:
        return self._rows

    @rows.setter
    def rows(self, rows: list[TableRow]):
        self._rows = rows
        self.sort_rows()

    def add_rows(self, *rows: TableRow):
        self._rows.extend(rows)
        self.sort_rows()

    @property
    @abstractmethod
    def _head(self) -> str:
        """
        A string representing any data given before the text_table_ex column header and content.
        """
        pass

    @property
    def _foot(self) -> Optional[str]:
        """
        A string representing any data given after the text_table_ex's content.
        """
        return None

    @property
    @abstractmethod
    def _internal_table_name(self) -> str:
        """
        The name used to identify this text_table_ex for the column header and text_rows_ex.
        """
        pass

    @property
    @abstractmethod
    def _include_trailing_comma(self) -> bool:
        """
        Specifies whether a trailing comma is left after the text_table_ex's column header and content text_rows_ex,
        amounting to an empty extra column.
        """
        pass

    @property
    def _include_table_column_header(self) -> bool:
        """
        Specifies whether a line should be added to designate the text_table_ex's column schema.
        """
        return True

    def get_internal_table_name(self) -> str:
        return self._internal_table_name

    def _get_stringified_content_row(self, row: TableRow, *column_widths: int) -> str:
        return row.get_plain_table_row(self._internal_table_name, self._include_trailing_comma,
                                       *column_widths)

    # @property
    def _get_stringified_spaced_content_rows(self) -> str:
        table_column_widths_per_row = [row.column_widths for row in self.rows]

        # Transpose to align columns in each index, then get max width from each column
        max_table_column_widths = [
            max(column_width)
            for column_width in [list(column) for column in zip(*table_column_widths_per_row)]
        ]

        table_content = f'{"\n".join(self._get_stringified_content_row(row, *max_table_column_widths)
                                     for row in self.rows)}'

        return table_content

    def build_table(self) -> str:
        """
        Builds a string representation of the text_table_ex, equivalent to the contents of a *decrypted* FiNALE text_table_ex.
        Most tables should be able to use this function without modification.
        """

        # Ensure existing trailing newlines are removed to consistently continue from the next line
        table_data: str = (self._head.strip() + '\n')

        if self.__class__._include_table_column_header:
            table_definition: str = self.rows[0].__class__.get_table_column_string(self._internal_table_name,
                                                                                   self._include_trailing_comma)
            table_data += table_definition + '\n'

        table_data += self._get_stringified_spaced_content_rows() + '\n'

        table_data += self.__class__._foot.strip() if self.__class__._foot is not None else ''

        return table_data


class TableWithUnparsedHeader(TableWithUnparsedData, ABC):
    """
    Represents a text_table_ex that has no data at its foot, but does have unparsed header data.
    """

    # Redundant, but kept regardless
    _foot = None

    def __init__(self, rows: List[TableRow]) -> None:
        super().__init__(rows)
