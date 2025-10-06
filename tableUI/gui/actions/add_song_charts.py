from PySide6.QtWidgets import QWidget, QMessageBox
from sqlmodel import Session, select

from tableUI.db.models import Chart, Song
from tableUI.gui.dialogues.edit_charts import ChartManagementDialog, ChartConfigProperties, ChartReconfigurationArgs


def addCharts(session: Session, song: Song | None, parent: QWidget = None):
    dialog = ChartManagementDialog(
        session=session,
        song=song,
        parent=parent,
    )

    dialog.chartConfigurationComplete.connect(
        lambda chart_reconfiguration_args: reconfigure_charts_in_db(session=session,
                                                                    charts=chart_reconfiguration_args,
                                                                    parent=parent)
    )

    dialog.open()

    return dialog

def reconfigure_charts_in_db(session: Session, charts: list[Chart], parent: QWidget = None):
    # print(chart_configs)

    try:
        # fresh_song = session.exec(
        #     select(Song).where(Song == chart_configs.song)
        # )
        for chart in charts:

            # chart = session.exec(
            #     select(Chart).
            #     where(Chart.difficulty_level == chart_props.chart_difficulty_level).
            #     where(Chart.chart_song == fresh_song)
            # ).one()

            session.add(chart)

            # print(chart.song_id)

            # chart.song_id = chart_configs.song.id
            # chart.affects_rating = chart_props.affects_rating
            # chart.difficulty_constant = chart_props.difficulty_constant
            # chart.creator = chart_props.chart_creator
            # session.add(chart)
        session.commit()
    except Exception as e:
        session.rollback()
        QMessageBox.critical(
            parent,
            'Error Adding Charts',
            f'An error has occurred while adding charts to the database. ({type(e)}: {e})'
        )
