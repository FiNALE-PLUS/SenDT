from tableUI.parsers.tables.table_types.abstract.row import TableRow
from tableUI.parsers.tables.table_types.abstract.table import TableWithUnparsedData
from tableUI.parsers.tables.textout.models import FilledMusicTextoutExTable, TextoutRow, FilledMusicTextoutJpTable


def validate_textout_table_lengths_equal(ex_table: FilledMusicTextoutExTable, jp_table: FilledMusicTextoutJpTable, row_type: str):
    if len(ex_table.rows) != len(jp_table.rows):
        row_diff = abs(len(ex_table.rows) - len(jp_table.rows))
        raise ValueError(f"The two textout tables provided do not have the same number of {row_type} rows within them "
                         f"- please add the {row_diff} missing {'row' if row_diff == 1 else 'rows'} to "
                         f"the {'EX' if len(ex_table.rows) < len(jp_table.rows) else 'JP'} table."
                         f"\n(textout_ex has {len(ex_table.rows)} {row_type} rows, "
                         f"textout_jp has {len(jp_table.rows)})")

def validate_row_ids_at_same_index(ex_row: TextoutRow, jp_row: TextoutRow, row_type: str):
    if ex_row.text_id != jp_row.text_id:
        raise ValueError(f"The two textout tables provided do not have {row_type} rows ordered identically. "
                         f"Fix table sorting before parsing into the database. "
                         f"\n(Got EX row ID `{ex_row.text_id}` at the same row index "
                         f"as JP row ID `{jp_row.text_id}`)")


def validate_generic_table_lengths_equal(*tables: TableWithUnparsedData):
    initial_length = len(tables[0].rows)

    for table in tables:
        if len(table.rows) != initial_length:
            raise ValueError(f"The tables provided to not have equal numbers of rows.\n"
                             f"(got: {', '.join([str(type(table)) + str(len(table.rows)) for table in tables])})\n)")


def validate_generic_ids_match(*ids: int):
    if not all(x == ids[0] for x in ids):
        raise ValueError(f"The IDs provided are not identical.\n"
                         f"(got: {', '.join(str(id_to_validate) for id_to_validate in ids)})\n")