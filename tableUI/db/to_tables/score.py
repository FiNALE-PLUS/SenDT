from sqlmodel import Session, select

from tableUI.db.models import Chart
from tableUI.parsers.tables.field_types.quoted_string import DoubleQuotedString
from tableUI.parsers.tables.table_types.score.models import ScoreTable, ScoreRow


def build_score_table_from_db(session: Session) -> ScoreTable:
    score_db_rows = session.exec(
        select(Chart).order_by(Chart.song_id).order_by(Chart.difficulty_level_id)
    ).fetchall()

    table_rows = []

    for row in score_db_rows:
        try:
            table_rows.append(ScoreRow(
                id=int(f'{row.song_id}{row.difficulty_level_id:02}'),
                name=f'eScore'
                     f'_{row.chart_song.id:03}'
                     f'_{DoubleQuotedString.remove_quotes(row.chart_song.filename)}'
                     f'_{row.difficulty_level_id:02}',
                chart_difficulty_constant=row.difficulty_constant,
                chart_creator_id=row.creator_id,
                affects_rating=row.affects_rating,
                internal_chart_name=DoubleQuotedString(f'{row.chart_song.id:03}'
                                                       f'_{DoubleQuotedString.remove_quotes(row.chart_song.filename)}'
                                                       f'_{row.difficulty_level_id:02}'),
            ))
        except AttributeError:
            print(row)

    return ScoreTable(table_rows)
