from PySide6.QtGui import Qt
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QRadioButton, QButtonGroup, QHBoxLayout, QComboBox
from sqlalchemy.exc import NoResultFound
from sqlmodel import select, Session

from db.models import Song, SongArtist
from tableUI.gui.widgets.form.lang_entry import GroupBoxedTextoutLangEntries
from tableUI.parsers.tables.field_types.quoted_string import TextoutQuotedString


class ArtistCreationError(ValueError):
    pass


class SongEditArtistPanel(QGroupBox):
    def __init__(self, session: Session, song: Song, song_in_db: bool, parent=None):
        super(SongEditArtistPanel, self).__init__(parent=parent, title='Artist')
        self.db_session = session
        self.song = song
        self.song_in_db = song_in_db

        self.new_song_artist_form_box = GroupBoxedTextoutLangEntries('New Artist', self)
        self.existing_song_artist_select = QComboBox()
        self.fill_existing_song_artist_select()
        self.existing_artist_options_box = QGroupBox('Existing Artist', self)
        existing_artist_options_layout = QVBoxLayout()
        existing_artist_options_layout.addWidget(self.existing_song_artist_select)
        self.existing_artist_options_box.setLayout(existing_artist_options_layout)

        artist_type_selection_layout = QHBoxLayout()
        artist_type_button_group = QButtonGroup(self)
        self.use_existing_artist_button = QRadioButton('Select Existing Artist')
        artist_type_button_group.addButton(self.use_existing_artist_button)
        self.use_new_artist_button = QRadioButton('Add New Artist')
        artist_type_button_group.addButton(self.use_new_artist_button)
        artist_type_button_group.buttonClicked.connect(self.process_artist_type_change)
        self.use_existing_artist_button.click()
        artist_type_selection_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        artist_type_selection_layout.addStretch(1)
        artist_type_selection_layout.addWidget(self.use_existing_artist_button)
        artist_type_selection_layout.addStretch(1)
        artist_type_selection_layout.addWidget(self.use_new_artist_button)
        artist_type_selection_layout.addStretch(1)

        self.fill_values()

        artist_selection_layout = QVBoxLayout()
        self.setLayout(artist_selection_layout)
        artist_selection_layout.addLayout(artist_type_selection_layout)
        artist_selection_layout.addWidget(self.existing_artist_options_box)
        artist_selection_layout.addWidget(self.new_song_artist_form_box)

    def getArtist(self) -> SongArtist:
        if self.use_existing_artist_button.isChecked():
            return self.existing_song_artist_select.currentData()
        else:
            english_name = TextoutQuotedString(self.new_song_artist_form_box.getEnglish())
            japanese_name = TextoutQuotedString(self.new_song_artist_form_box.getJapanese())
            try:
                return self.db_session.exec(
                    select(SongArtist).
                    where(SongArtist.name_en == english_name).
                    where(SongArtist.name_jp == japanese_name)
                ).one()
            except NoResultFound:
                return SongArtist(
                    name_en=english_name,
                    name_jp=japanese_name
                )
            except Exception as e:
                raise ArtistCreationError('error attempting to search for an identical artist') from e


    def process_artist_type_change(self):
        if self.use_existing_artist_button.isChecked():
            self.new_song_artist_form_box.setEnabled(False)
            self.existing_artist_options_box.setEnabled(True)
        elif self.use_new_artist_button.isChecked():
            self.new_song_artist_form_box.setEnabled(True)
            self.existing_artist_options_box.setEnabled(False)
        else:
            raise RuntimeError("Invalid artist type selected")

    def get_artists_from_db(self):
        return self.db_session.exec(select(SongArtist).order_by(SongArtist.name_en)).all()

    def fill_existing_song_artist_select(self):
        for artist in self.get_artists_from_db():
            truncated_name = TextoutQuotedString.remove_quotes(artist.name_en)[:50]
            self.existing_song_artist_select.addItem(
                f'{truncated_name}{"..." if len(artist.name_en) > 50 else ""}', artist)
        if self.song_in_db:
            artist_index = self.existing_song_artist_select.findData(self.song.artist)
            self.existing_song_artist_select.setCurrentIndex(artist_index)

    def fill_values(self):
        if (artist := self.song.artist) is not None:
            if artist.name_en is not None:
                self.new_song_artist_form_box.setEnglish(TextoutQuotedString.remove_quotes(self.song.artist.name_en))
            if artist.name_jp is not None:
                self.new_song_artist_form_box.setJapanese(TextoutQuotedString.remove_quotes(self.song.artist.name_jp))