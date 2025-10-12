from typing import NamedTuple

from PySide6.QtWidgets import QWidget, QGroupBox, QCheckBox

from tableUI.gui.widgets.utils.layouts.flag_layout import get_checkbox_grid_layout


class BackupFileTypesFlags(NamedTuple):
    tables: bool
    charts: bool
    cover_art: bool
    bg_videos: bool
    audio: bool


class BackupFileTypesFlagPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('File Types to Back Up')

        self.table_box = QCheckBox('Tables')
        self.chart_box = QCheckBox('Charts')
        self.cover_art_box = QCheckBox('Cover Art')
        self.bg_video_box = QCheckBox('Background Videos')
        self.audio_box = QCheckBox('Audio')

        self.setLayout(get_checkbox_grid_layout(
            2,
            self.table_box,
            self.chart_box,
            self.cover_art_box,
            self.bg_video_box,
            self.audio_box
        ))

    def getFlags(self):
        return BackupFileTypesFlags(
            tables=self.table_box.isChecked(),
            charts=self.chart_box.isChecked(),
            cover_art=self.cover_art_box.isChecked(),
            bg_videos=self.bg_video_box.isChecked(),
            audio=self.audio_box.isChecked()
        )

    def setFlags(self, flags: BackupFileTypesFlags):
        self.table_box.setChecked(flags.tables)
        self.chart_box.setChecked(flags.charts)
        self.cover_art_box.setChecked(flags.cover_art)
        self.bg_video_box.setChecked(flags.bg_videos)
        self.audio_box.setChecked(flags.audio)
