from typing import NamedTuple

from PySide6.QtWidgets import QGridLayout, QGroupBox, QCheckBox

from db.models import Song


class SongFlagPair(NamedTuple):
    data: bool | None
    checkbox: QCheckBox


class SongFlags(NamedTuple):
    re_master: bool
    dress: bool
    darkness: bool
    miles_counted: bool
    vl: bool
    recording_enabled: bool
    special_preview: bool


class SongEditFlagPanel(QGroupBox):
    def __init__(self, song: Song, parent=None):
        super(SongEditFlagPanel, self).__init__(parent=parent, title='Flags')
        self.song = song

        boolean_flag_layout = QGridLayout()
        self.setLayout(boolean_flag_layout)
        self.remaster_enabled = QCheckBox('Includes Re:MASTER')
        boolean_flag_layout.addWidget(self.remaster_enabled, 0, 0)
        self.dress_enabled = QCheckBox('Dress')
        boolean_flag_layout.addWidget(self.dress_enabled, 0, 1)
        self.darkness_enabled = QCheckBox('Darkness')
        boolean_flag_layout.addWidget(self.darkness_enabled, 0, 2)
        self.mile_count_enabled = QCheckBox('Miles Counted')
        boolean_flag_layout.addWidget(self.mile_count_enabled, 1, 0)
        self.vl_enabled = QCheckBox('VL')
        boolean_flag_layout.addWidget(self.vl_enabled, 1, 1)
        self.recording_enabled = QCheckBox('Play Recording')
        boolean_flag_layout.addWidget(self.recording_enabled, 1, 2)
        self.special_preview_enabled = QCheckBox('Special Preview')
        boolean_flag_layout.addWidget(self.special_preview_enabled, 2, 0)
        self.setup_flag_boxes()

    def getSongFlags(self) -> SongFlags:
        return SongFlags(
            re_master=self.remaster_enabled.isChecked(),
            dress=self.dress_enabled.isChecked(),
            darkness=self.darkness_enabled.isChecked(),
            miles_counted=self.mile_count_enabled.isChecked(),
            vl=self.vl_enabled.isChecked(),
            recording_enabled=self.recording_enabled.isChecked(),
            special_preview=self.special_preview_enabled.isChecked(),
        )

    def setup_flag_boxes(self):
        self.recording_enabled.setChecked(True)
        if self.song.re_master is not None:
            self.remaster_enabled.setChecked(self.song.re_master != 99999999)

        song_data_pairs = (
            SongFlagPair(self.song.dress, self.dress_enabled),
            SongFlagPair(self.song.darkness, self.darkness_enabled),
            SongFlagPair(self.song.miles_counted, self.mile_count_enabled),
            SongFlagPair(self.song.vl, self.vl_enabled),
            SongFlagPair(self.song.play_recording_enabled, self.recording_enabled),
            SongFlagPair(self.song.special_pv, self.special_preview_enabled),
        )

        for pair in song_data_pairs:
            if pair.data is not None:
                pair.checkbox.setChecked(pair.data)
