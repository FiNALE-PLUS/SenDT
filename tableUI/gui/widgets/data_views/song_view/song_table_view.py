from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton
from sqlmodel import Session, select

from db.models import Song
from tableUI.gui.actions.add_song import addSong
from tableUI.gui.widgets.data_views.song_view.song_view import SongView


class SongTableView(QScrollArea):
    def __init__(self, session: Session, modded_only: bool = True):
        super().__init__()
        self.db_session = session
        self.modded_only = modded_only
        self.setWidgetResizable(True)

        self.internalWidget = QWidget()
        self.internalLayout = QVBoxLayout(self.internalWidget)

        self.internalLayout.addStretch(100)
        self.rebuild_table_view()
        # Stretch is added only on initialisation, and is always used throughout subsequent rebuilds

        self.internalWidget.setLayout(self.internalLayout)
        self.setWidget(self.internalWidget)

    def rebuild_table_view(self):
        query = select(Song).order_by(Song.id.asc())
        if self.modded_only:
            query = query.where(Song.is_vanilla == False)

        songs = self.db_session.exec(query).all()

        for i in reversed(range(self.internalLayout.count())):
            widgetToRemove = self.internalLayout.itemAt(i).widget()
            if widgetToRemove is not None:
                # remove it from the layout list
                self.internalLayout.removeWidget(widgetToRemove)
                # remove it from the gui
                widgetToRemove.setParent(None)

        for song in songs:
            song_view = SongView(song, self.db_session)
            song_view.songEdited.connect(self.rebuild_table_view)
            song_view.chartsEdited.connect(self.rebuild_table_view)
            song_view.songRemoved.connect(self.rebuild_table_view)
            self.internalLayout.insertWidget(self.internalLayout.count() - 1, song_view)
            # self.internalLayout.addWidget(song_view)

    def filterSongs(self, search_term: str):
        # self.setUpdatesEnabled(False)
        for widget_index in range(self.internalLayout.count()):
            song_widget = self.internalLayout.itemAt(widget_index).widget()

            # Ignore the stretch item
            if song_widget is not None:
                if not search_term:
                    song_widget.setVisible(True)
                else:
                    song_widget.setVisible(
                        search_term.lower() in song_widget.getTitle().lower()
                        or search_term.lower() in song_widget.getSubtitle().lower()
                    )
        # self.setUpdatesEnabled(True)


class SearchableSongTableView(QWidget):
    def __init__(self, session: Session, modded_only: bool = True):
        super().__init__()
        self.db_session = session
        self.modded_only = modded_only

        widget_layout = QVBoxLayout()

        entry_layout = QFormLayout()
        self.title_entry = QLineEdit()
        self.title_entry.setToolTip('Filters songs by song and artist names')
        entry_layout.addRow('Search:', self.title_entry)
        widget_layout.addLayout(entry_layout)

        self.table_view = SongTableView(self.db_session, self.modded_only)
        widget_layout.addWidget(self.table_view)

        self.add_song_button = QPushButton('Add New Song')
        widget_layout.addWidget(self.add_song_button)

        self.title_entry.textChanged.connect(lambda: self.table_view.filterSongs(self.title_entry.text()))
        self.add_song_button.clicked.connect(self.addSongFromTable)

        self.setLayout(widget_layout)

    def addSongFromTable(self):
        dialog = addSong(
            session=self.db_session,
            song=None,
            parent=self,
        )

        dialog.songConfigurationComplete.connect(self.table_view.rebuild_table_view)

