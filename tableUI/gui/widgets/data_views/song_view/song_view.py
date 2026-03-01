import shutil

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QFrame, QSizePolicy, QPushButton, QHBoxLayout, \
    QMessageBox
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from db.models import Song
from tableUI.gui.actions.add_song import addSong
from tableUI.gui.actions.add_song_charts import addCharts
from tableUI.gui.stylesheets.frame import get_outlined_frame_stylesheet
from tableUI.gui.widgets.data_views.song_view.components.cover_art_and_bg_video_view import CoverArtDisplayWithBGVideoPreview
from tableUI.gui.widgets.data_views.song_view.components.song_difficulty_view import SongDifficultyView
from tableUI.gui.widgets.utils.titles import FinaleSongTitleWidget
from tableUI.parsers.tables.field_types.quoted_string import TextoutQuotedString, DoubleQuotedString
from tableUI.paths import get_user_data_dir_for


class SongView(QFrame):

    songEdited = Signal()
    chartsEdited = Signal()
    songRemoved = Signal()

    def __init__(self, song: Song, session: Session):
        super().__init__()
        # self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # self.setAttribute(Qt.WidgetAttribute.WA_, True)
        self.setObjectName('SongView')
        # Add background styling to the back of the entire frame, but not its children
        self.setStyleSheet(
            get_outlined_frame_stylesheet(self.objectName())
        )

        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))


        self.title_widget = FinaleSongTitleWidget('Song', 'Artist', 'placeholder')
        self.song = song
        self.db_session = session

        self.cover_art_widget = CoverArtDisplayWithBGVideoPreview(self.song)


        main_layout = QVBoxLayout()
        # header = QHeaderView(Orientation)
        info_layout = QHBoxLayout()
        info_layout.addLayout(self.cover_art_widget)
        info_layout.addWidget(self.title_widget, stretch=1)
        info_layout.addWidget(SongDifficultyView(self.song), stretch=2)

        main_layout.addLayout(info_layout)

        button_layout = QHBoxLayout()
        self.edit_song_button = QPushButton('Edit Song')
        button_layout.addWidget(self.edit_song_button)
        self.edit_charts_button = QPushButton('Edit Charts')
        button_layout.addWidget(self.edit_charts_button)
        self.remove_button = QPushButton('Remove')
        button_layout.addWidget(self.remove_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.edit_song_button.clicked.connect(self.handleSongEdit)
        self.edit_charts_button.clicked.connect(self.handleChartsEdit)
        self.remove_button.clicked.connect(self.handleRemove)

    def getTitle(self):
        return self.title_widget.title_text

    def getSubtitle(self):
        return self.title_widget.subtitle_text


    def handleSongEdit(self):
        song_dialog = addSong(
            session=self.db_session,
            song=self.song,
            parent=self,
        )

        song_dialog.songConfigurationComplete.connect(lambda _: self.songEdited.emit())

    def handleChartsEdit(self):
        chart_dialog = addCharts(
            session=self.db_session,
            song=self.song,
            parent=self
        )

        chart_dialog.chartConfigurationComplete.connect(lambda _: self.chartsEdited.emit())

    def handleRemove(self):
        if QMessageBox.question(
            self,
            'Remove Song?',
            'Are you sure you want to permanently remove this song? '
            'This will delete all data associated with the song.',
            defaultButton=QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            try:
                if self.db_session.exec(select(Song.is_vanilla).where(Song.id == self.song.id)).one():
                    QMessageBox.critical(
                        self,
                        'Vanilla Song Edit Attempt',
                        'Songs that are from the vanilla Maimai FiNALE songlist cannot be reconfigured.'
                    )
                    return
            except NoResultFound:
                pass

            try:
                self.db_session.delete(self.song)
                self.db_session.commit()

                song_cover_art_path = get_user_data_dir_for(self.song.id)
                if song_cover_art_path.exists():
                    shutil.rmtree(song_cover_art_path)

                self.songRemoved.emit()
                QMessageBox.information(self, 'Song Removal Successful',
                                        'The song has been successfully removed from the database.'
                                        )
            except Exception as e:
                self.db_session.rollback()
                QMessageBox.critical(self,
                                     'Error Deleting Song',
                                     f'An error occured when attempting to delete the song. ({type(e)}: {e})')

    @property
    def song(self):
        return self._song

    @song.setter
    def song(self, song: Song):
        self._song = song
        self.update()

    def update(self):
        self.title_widget.title_text = self.get_box_title()
        self.title_widget.subtitle_text = self.get_box_subtitle()
        self.title_widget.safename_text = self.get_box_safename()

    def get_box_title(self) -> str:
        return f'{TextoutQuotedString.remove_quotes(self.song.name_en)}'

    def get_box_subtitle(self) -> str:
        return f'{TextoutQuotedString.remove_quotes(self.song.artist.name_en)}'

    def get_box_safename(self) -> str:
        return DoubleQuotedString.remove_quotes(self.song.filename)


