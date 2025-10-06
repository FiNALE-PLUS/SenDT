from pathlib import Path
from typing import Iterable

from PIL import Image
from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QFormLayout, \
    QSpinBox, QComboBox, QGroupBox, QDoubleSpinBox, QMessageBox
from sqlalchemy import func
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from tableUI.db.models import Song, SongGenre
from tableUI.utils.assets.song_cover.dds.convert import save_cover_textures_from_image
from tableUI.gui.widgets.edit_song.artist_panel import SongEditArtistPanel
from tableUI.gui.widgets.edit_song.flag_panel import SongEditFlagPanel
from tableUI.gui.widgets.files.file_select import ImageSelectRow
from tableUI.gui.widgets.form.double_range import DoubleRangeSpinBoxes
from tableUI.gui.widgets.form.lang_entry import GroupBoxedTextoutLangEntries
from tableUI.parsers.tables.field_types.quoted_string import TextoutQuotedString
from tableUI.parsers.tables.field_types.utils.safename import safename_from_song_name
from tableUI.paths import get_user_data_cover_art_dir_for


class SongManagementDialog(QDialog):

    songConfigurationComplete = Signal(Song)

    def __init__(self, session: Session, song: Song | None, parent=None):
        super().__init__(parent)


        self.song_in_db = False
        self.db_session = session

        if song is not None:
            self.song = song
            try:
                song_exists_check = session.exec(select(Song).where(Song.id == self.song.id)).one()
                self.song_in_db = True
            except NoResultFound:
                pass
            window_title = f'Edit Song - {TextoutQuotedString.remove_quotes(self.song.name_en)}'
        else:
            window_title = f'Create Song'
            self.song = Song()
        self.setWindowTitle(window_title)

        # Accept & Reject buttons
        self.buttonBox = QHBoxLayout()
        self.buttonBox.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.add_completion_buttons_to_button_box()

        # Song editing Form
        song_info_layout = QVBoxLayout()
        song_data_layout = QVBoxLayout()
        song_edit_layout = QHBoxLayout()
        song_edit_layout.addLayout(song_info_layout, 1)
        song_edit_layout.addLayout(song_data_layout, 1)
        main_data_form = QFormLayout()

        ### Song ID
        self.song_id_select = QComboBox(self)
        for available_song_id in self.get_possible_song_ids():
            self.song_id_select.addItem(str(available_song_id), available_song_id)
        main_data_form.addRow('Song ID:', self.song_id_select)
        if self.song_in_db:
            self.song_id_select.setEnabled(False)
            self.song_id_select.setToolTip('An existing song\'s ID cannot be changed.')

        ### Cover Art
        self.cover_art_file_select = ImageSelectRow()
        main_data_form.addRow('Cover Art Image:', self.cover_art_file_select)

        ### BPM
        self.bpm_select = QDoubleSpinBox()
        self.setup_bpm_select()
        main_data_form.addRow('BPM:', self.bpm_select)
        song_info_layout.addLayout(main_data_form)
        # id_select_form_layout.addLayout(id_form)

        ### Sort IDs
        sort_id_box = QGroupBox('Sort IDs')
        sort_id_layout = QFormLayout()
        sort_id_box.setLayout(sort_id_layout)
        self.sort_id_select = QSpinBox()
        self.setup_sort_id_select()
        sort_id_layout.addRow('Sort ID:', self.sort_id_select)
        self.eng_sort_idx_select = QSpinBox()
        self.jp_sort_idx_select = QSpinBox()
        sort_id_layout.addRow('English sort index:', self.eng_sort_idx_select)
        sort_id_layout.addRow('Japanese sort index:', self.jp_sort_idx_select)
        self.setup_sort_idx_boxes()
        song_info_layout.addWidget(sort_id_box)

        ## Song safename
        self.song_title_form_box = GroupBoxedTextoutLangEntries('Song Title', self)
        song_info_layout.addWidget(self.song_title_form_box)

        ## Song Artist
        # artist_selection_box = QGroupBox('Artist', self)
        self.artist_selection_box = SongEditArtistPanel(
            session=self.db_session,
            song=self.song,
            song_in_db=self.song_in_db,
        )
        song_info_layout.addWidget(self.artist_selection_box)

        ## Miscellaneous data

        miscellaneous_layout = QFormLayout()
        miscellaneous_box = QGroupBox('Miscellaneous', self)
        miscellaneous_box.setLayout(miscellaneous_layout)
        song_data_layout.addWidget(miscellaneous_box)
        ### Song Genre
        self.genre_select = QComboBox()
        self.fill_genre_select()
        miscellaneous_layout.addRow('Genre:', self.genre_select)
        ### Game Version
        self.version_select = QSpinBox()
        self.setup_version_select()
        miscellaneous_layout.addRow('Version:', self.version_select)
        ### Subcategory
        self.subcategory_select = QComboBox()
        self.setup_subcategory_select()
        miscellaneous_layout.addRow('Subcategory:', self.subcategory_select)
        ### TODO: Event ID in window but disabled since it is *currently* unused for modded content
        self.event_id_select = QComboBox()
        self.setup_event_id_select()
        miscellaneous_layout.addRow('Event ID:', self.event_id_select)
        ### Preview time
        self.preview_range = DoubleRangeSpinBoxes()
        self.preview_range.setMutualMinimum(0)
        self.preview_range.setMutualMaximum(500)
        self.preview_range.setSingleStep(1)
        self.setup_preview_range()
        miscellaneous_layout.addRow('Menu Preview Range:', self.preview_range)

        #### START OF DISABLED VALUES
        unknown_values_tooltip = 'Editing disabled due to effects being unknown.'
        ### Song length
        self.song_length_override_entry = QSpinBox()
        self.song_length_override_entry.setEnabled(False)
        self.song_length_override_entry.setToolTip(unknown_values_tooltip)
        miscellaneous_layout.addRow('Song Length Override:', self.song_length_override_entry)
        ### Off Ranking
        self.off_ranking_entry = QSpinBox()
        self.off_ranking_entry.setEnabled(False)
        self.off_ranking_entry.setToolTip(unknown_values_tooltip)
        miscellaneous_layout.addRow('Off Ranking:', self.off_ranking_entry)
        ### AD Def
        self.ad_def_entry = QSpinBox()
        self.ad_def_entry.setEnabled(False)
        self.ad_def_entry.setToolTip(unknown_values_tooltip)
        miscellaneous_layout.addRow('Ad Def:', self.ad_def_entry)
        ### Challenge Track
        self.challenge_track_entry = QSpinBox()
        self.challenge_track_entry.setEnabled(False)
        self.challenge_track_entry.setToolTip(unknown_values_tooltip)
        miscellaneous_layout.addRow('Challenge Track:', self.challenge_track_entry)
        ### Bonus
        self.bonus_entry = QSpinBox()
        self.bonus_entry.setEnabled(False)
        self.bonus_entry.setToolTip(unknown_values_tooltip)
        miscellaneous_layout.addRow('Bonus:', self.bonus_entry)

        self.setup_disabled_values()
        #### END OF DISABLED VALUES
        ### Boolean Flags
        self.song_flag_edit_panel = SongEditFlagPanel(song=self.song)
        song_data_layout.addWidget(self.song_flag_edit_panel)

        # song_edit_widget = QWidget()
        # song_edit_widget.setLayout(song_edit_layout)
        # dialog_tabs = QTabWidget(self)
        # dialog_tabs.addTab(song_edit_widget, 'Edit &Song')
        # dialog_tabs.addTab(QLabel("TODO"), 'Edit &Charts')
        dialog_layout = QVBoxLayout()
        dialog_layout.addLayout(song_edit_layout)
        dialog_layout.addLayout(self.buttonBox)
        self.setLayout(dialog_layout)
        self._fill_form_from_song()

    @Slot()
    def validate_song_configuration_to_accept(self):
        english_name = self.song_title_form_box.getEnglish()
        japanese_name = self.song_title_form_box.getJapanese()

        if not english_name or not japanese_name:
            QMessageBox.warning(self, 'Song Misconfigured',
                                'One or both song titles have been left empty. '
                                'Please enter a song safename for both languages before continuing.')
            return

        cur_artist = self.artist_selection_box.getArtist()
        if (TextoutQuotedString.remove_quotes(cur_artist.name_en) == ''
                or TextoutQuotedString.remove_quotes(cur_artist.name_jp) == ''):
            QMessageBox.warning(self, 'Song Misconfigured',
                                'One or both artist names have been left empty. '
                                'Please enter a artist name for both languages before continuing.')
            return

        preview_range = self.preview_range.getRange()
        preview_length = preview_range.upper_bound - preview_range.lower_bound
        if preview_length <= 1:
            QMessageBox.warning(self, 'Song Misconfigured',
                                'The preview length of the song is too short. '
                                'Please select a later preview end time before continuing.')
            return

        self.fill_song_from_form()

    @Slot()
    def fill_song_from_form(self):
        """
        Configures the internal song object using the values provided in the dialog's form,
        before emitting ``songConfigurationComplete`` to pass the configured song to the caller.
        :return:
        """

        cover_art_path_text = self.cover_art_file_select.getFilePath()
        if cover_art_path_text:
            cover_art_path = Path(cover_art_path_text)
            if cover_art_path.exists():
                cover_art_img = Image.open(cover_art_path)
                output_dir = get_user_data_cover_art_dir_for(self.song_id_select.currentData())
                output_dir.mkdir(parents=True, exist_ok=True)
                save_cover_textures_from_image(cover_art_img, output_dir)

        try:
            if self.db_session.exec(select(Song.is_vanilla).where(Song.id == self.song_id_select.currentData())).one():
                QMessageBox.critical(
                    self,
                    'Vanilla Song Edit Attempt',
                    'Songs that are from the vanilla Maimai FiNALE songlist cannot be reconfigured.'
                )
                return
        except NoResultFound:
            self.song.is_vanilla = False

        # ID & BPM
        self.song.id = self.song_id_select.currentData()
        self.song.bpm = self.bpm_select.value()
        # Sort IDs
        self.song.sort_id = self.sort_id_select.value()
        self.song.sort_ex_index = self.eng_sort_idx_select.value()
        self.song.sort_jp_index = self.jp_sort_idx_select.value()

        # Name & Artist
        self.song.name_en = TextoutQuotedString(self.song_title_form_box.getEnglish())
        self.song.name_jp = TextoutQuotedString(self.song_title_form_box.getJapanese())
        self.song.filename = safename_from_song_name(self.song_title_form_box.getEnglish(),
                                                     self.song_id_select.currentData())
        self.song.artist = self.artist_selection_box.getArtist()

        #Miscellaneous
        self.song.genre = self.genre_select.currentData()
        self.song.version = self.version_select.value()
        self.song.sub_category = self.subcategory_select.currentData()
        self.song.event_id = self.event_id_select.currentData()
        preview_range = self.preview_range.getRange()
        self.song.preview_start_time = preview_range.lower_bound
        self.song.preview_end_time = preview_range.upper_bound
        self.song.song_length_override = self.song_length_override_entry.value()
        self.song.off_ranking = self.off_ranking_entry.value()
        self.song.ad_def = self.ad_def_entry.value()
        self.song.challenge_track = self.challenge_track_entry.value()
        self.song.bonus = self.bonus_entry.value()

        # Flag checkboxes
        song_flags = self.song_flag_edit_panel.getSongFlags()
        self.song.re_master = 0 if song_flags.re_master else 99999999
        self.song.dress = song_flags.dress
        self.song.darkness = song_flags.darkness
        self.song.miles_counted = song_flags.miles_counted
        self.song.vl = song_flags.vl
        self.song.play_recording_enabled = song_flags.recording_enabled
        self.song.special_pv = song_flags.special_preview

        # Emit configured song to be added to DB
        self.songConfigurationComplete.emit(self.song)
        self.accept()

    def setup_bpm_select(self):
        self.bpm_select.setMinimum(0)
        self.bpm_select.setMaximum(1000)
        if self.song.bpm is None:
            self.bpm_select.setValue(60)
        else:
            self.bpm_select.setValue(self.song.bpm)

    def setup_disabled_values(self):
        if self.song.song_length_override is not None:
            self.song_length_override_entry.setValue(self.song.song_length_override)
        if self.song.off_ranking is not None:
            self.off_ranking_entry.setValue(self.song.off_ranking)
        if self.song.ad_def is not None:
            self.ad_def_entry.setValue(self.song.ad_def)
        if self.song.challenge_track is not None:
            self.challenge_track_entry.setValue(self.song.challenge_track)
        if self.song.bonus is not None:
            self.bonus_entry.setValue(self.song.bonus)

    def setup_preview_range(self):
        if self.song.preview_start_time is not None:
            self.preview_range.setLowerBound(self.song.preview_start_time)
        if self.song.preview_end_time is not None:
            self.preview_range.setUpperBound(self.song.preview_end_time)

    def setup_event_id_select(self):
        self.event_id_select.setEnabled(False)
        self.event_id_select.setToolTip('Currently disabled while custom events are not implemented')
        event_ids = self.db_session.exec(
            select(Song.event_id).group_by(Song.event_id).order_by(Song.event_id.desc())
        ).all()

        for event_id in event_ids:
            self.event_id_select.addItem(str(event_id), event_id)

        self.event_id_select.setCurrentIndex(self.event_id_select.findData(0))

    def setup_sort_id_select(self):
        self.sort_id_select.setMinimum(100000)
        self.sort_id_select.setMaximum(
            self.db_session.exec(select(func.max(Song.sort_id))).one() + 1
        )
        if self.song.sort_id is not None:
            self.sort_id_select.setValue(self.song.sort_id)
        else:
            # TODO: Sort ID is descending from knowledge - check
            self.sort_id_select.setValue(
                self.db_session.exec(select(func.min(Song.sort_id))).one() - 1
            )

    def setup_sort_idx_boxes(self):
        self.eng_sort_idx_select.setMinimum(0)
        self.jp_sort_idx_select.setMinimum(0)
        self.eng_sort_idx_select.setMaximum(
            self.db_session.exec(select(func.max(Song.sort_ex_index))).one() + 1
        )
        self.jp_sort_idx_select.setMaximum(
            self.db_session.exec(select(func.max(Song.sort_jp_index))).one() + 1
        )

        if self.song.sort_ex_index is not None:
            self.eng_sort_idx_select.setValue(self.song.sort_ex_index)
        else:
            self.eng_sort_idx_select.setValue(
                self.db_session.exec(select(func.min(Song.sort_ex_index))).one() - 1
            )
        if self.song.sort_jp_index is not None:
            self.jp_sort_idx_select.setValue(self.song.sort_jp_index)
        else:
            self.jp_sort_idx_select.setValue(
                self.db_session.exec(select(func.min(Song.sort_jp_index))).one() - 1
            )


    def fill_genre_select(self):
        genres = self.db_session.exec(select(SongGenre).order_by(SongGenre.id)).all()

        for genre in genres:
            self.genre_select.addItem(genre.name_en, genre)
        if self.song_in_db:
            genre_index = self.genre_select.findData(self.song.genre)
            self.genre_select.setCurrentIndex(genre_index)

    def setup_version_select(self):
        min_game_version = self.db_session.exec(select(func.min(Song.version))).one()
        max_game_version = self.db_session.exec(select(func.max(Song.version))).one()
        self.version_select.setMinimum(min_game_version)
        self.version_select.setMaximum(max_game_version + 1000)

        if self.song.version:
            self.version_select.setValue(self.song.version)
        else:
            self.version_select.setValue(max_game_version)

    def setup_subcategory_select(self):
        subcategory_values = self.db_session.exec(
            select(Song.sub_category).group_by(Song.sub_category).order_by(Song.sub_category.desc())
        ).fetchall()
        for val in subcategory_values:
            self.subcategory_select.addItem(str(val), val)

        if self.song.sub_category is not None:
            self.subcategory_select.setCurrentIndex(
                self.subcategory_select.findData(self.song.sub_category)
            )
        else:
            self.subcategory_select.setCurrentIndex(
                self.subcategory_select.findData(0)
            )

    def _fill_form_from_song(self):
        if self.song.id is not None:
            self.song_id_select.setCurrentText(str(self.song.id))

        if self.song.name_en is not None:
            self.song_title_form_box.setEnglish(TextoutQuotedString.remove_quotes(self.song.name_en))
        if self.song.name_jp is not None:
            self.song_title_form_box.setJapanese(TextoutQuotedString.remove_quotes(self.song.name_jp))

    def get_possible_song_ids(self) -> Iterable[int]:
        existing_song_id_statement = select(Song.id).order_by(Song.id)

        if self.song_in_db:
            existing_song_id_statement = existing_song_id_statement.where(Song.id != self.song.id)

        disallowed_ids = self.db_session.exec(existing_song_id_statement).all()

        allowed_ids = []

        for i in range(1, 1000):
            if i not in disallowed_ids:
                allowed_ids.append(i)

        return allowed_ids

    def build_song(self) -> Song:
        name_en = TextoutQuotedString('english safename')
        name_jp = TextoutQuotedString('japanese safename')

        return Song()

    def add_completion_buttons_to_button_box(self):
        accept_button = QPushButton("Accept")
        accept_button.clicked.connect(self.validate_song_configuration_to_accept)
        reject_button = QPushButton("Cancel")
        reject_button.clicked.connect(self.reject)
        self.buttonBox.addStretch()
        self.buttonBox.addWidget(accept_button)
        self.buttonBox.addWidget(reject_button)


