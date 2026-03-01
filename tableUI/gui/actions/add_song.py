from PySide6.QtWidgets import QWidget, QMessageBox
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from db.models import Song, ChartDifficultyLevel, Chart
from tableUI.gui.dialogues.edit_song import SongManagementDialog
from utils.finale.difficulties import FinaleChartDifficulty
from utils.finale.flags import REMASTER_DISABLED


# TODO: Add default charts, including Re:MASTER if selected
def addSong(session: Session, song: Song | None, parent: QWidget = None):
    dialog = SongManagementDialog(
        session=session,
        song=song,
        parent=parent,
    )

    dialog.songConfigurationComplete.connect(
        lambda new_song: add_song_to_db(session=session, song=new_song, parent=parent)
    )

    dialog.open()

    return dialog


def add_song_to_db(session: Session, song: Song, parent: QWidget = None):
    try:
        session.add(song)

        charts = song.song_charts
        required_difficulties = [diff.name for diff in (
            FinaleChartDifficulty.EASY,
            FinaleChartDifficulty.BASIC,
            FinaleChartDifficulty.ADVANCED,
            FinaleChartDifficulty.EXPERT,
            FinaleChartDifficulty.MASTER,
        )]

        # Add a fresh Re:MASTER chart if necessary
        if song.re_master != REMASTER_DISABLED:
            required_difficulties.append(FinaleChartDifficulty.RE_MASTER.name)
        # Remove the Re:MASTER chart from the Database when it is not required but exists
        # TODO: Move to event to make universal within UI?
        #  (Only necessary if chart panel can control base chart availability,
        #  which would mean it also can control flags)
        else:
            try:
                extra_remaster_chart = session.exec(select(Chart).
                                                    where(Chart.difficulty_level_id == FinaleChartDifficulty.RE_MASTER.value).
                                                    where(Chart.song_id == song.id)).one()

                session.delete(extra_remaster_chart)
            except NoResultFound:
                pass

        # Add a new chart for the required difficulty if they don't yet exist
        for chart in charts:
            if chart.difficulty_level.name in required_difficulties:
                required_difficulties.remove(chart.difficulty_level.name)
        for remaining_difficulty_name in required_difficulties:
            difficulty_level = session.exec(select(ChartDifficultyLevel).
                                            where(ChartDifficultyLevel.name == remaining_difficulty_name)).one()
            # chart_id = get_chart_id_from_song_and_difficulty(song, difficulty_level)

            session.add(
                Chart(
                    # id=chart_id,
                    song=song,
                    song_id=song.id,
                    difficulty_level=difficulty_level,
                    difficulty_constant=1,
                    affects_rating=False,
                )
            )

        session.commit()

        QMessageBox.information(
            parent,
            'Song Added Successfully',
            'The song has been successfully added to the database.'
        )
    except Exception as e:
        session.rollback()
        QMessageBox.critical(
            parent,
            'Error Adding Song',
            f'An error has occurred while adding the song to the database. ({type(e)}: {e})'
        )
