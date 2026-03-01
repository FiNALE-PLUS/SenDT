from pathlib import Path

from PySide6.QtGui import QPixmap, Qt, QFont
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QFrame, QVBoxLayout

from db.models import Song
from tableUI.gui.img.pixmap.difficulties import BASE_DIFF_30PX_PIXMAPS, UTAGE_DIFF_30PX_PIXMAPS
from tableUI.gui.stylesheets.frame import get_highlight_outlined_frame_stylesheet
from tableUI.parsers.tables.field_types.quoted_string import TextoutQuotedString


class SingleSongDifficultyDisplay(QHBoxLayout):
    label_font = QFont()
    # label_font.setBold(True)
    label_font.setPointSize(10)
    def __init__(self, img_path: Path, difficulty_text: str, chart_creator: str = None):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        img_label = QLabel()
        img_pixmap = QPixmap(str(img_path))
        img_label.setPixmap(img_pixmap)
        self.addWidget(img_label)
        # self.setAlignment()


        text_layout = QVBoxLayout()
        text_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        diff_text_layout = QHBoxLayout()
        diff_text_layout.addStretch()
        diff_text_label = QLabel()
        diff_text_label.setFont(self.label_font)
        diff_text_label.setText(difficulty_text)
        diff_text_layout.addWidget(diff_text_label)
        diff_text_layout.addStretch()

        text_layout.addLayout(diff_text_layout)

        if chart_creator is not None:
            creator_layout = QHBoxLayout()
            creator_layout.addStretch()
            creator_label = QLabel(f'({chart_creator})')
            # creator_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            creator_label.setFont(self.label_font)
            creator_layout.addWidget(creator_label)
            creator_layout.addStretch()
            text_layout.addLayout(creator_layout)
        # text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.addLayout(text_layout)

class SongDifficultyView(QFrame):
    def __init__(self, song: Song, columns: int = 3, parent=None):
        super(SongDifficultyView, self).__init__(parent)
        self.song = song
        self.setObjectName('DiffView')
        # Add background styling to the back of the entire frame, but not its children
        self.setStyleSheet(
            get_highlight_outlined_frame_stylesheet(self.objectName())
        )

        layout = QGridLayout()
        self.setLayout(layout)


        for i, difficulty_display in enumerate(self.get_song_difficulty_displays()):
            layout.addLayout(difficulty_display, i//columns, i%columns)

    def get_song_difficulty_displays(self):
        displays = []
        charts = self.song.song_charts

        for chart in charts:
            difficulty_img_path = None
            difficulty_constant = chart.difficulty_constant
            if difficulty_constant == 0:
                diff_text = '!'
            else:
                diff_text = str(
                    int(difficulty_constant) if difficulty_constant % 1 == 0 else difficulty_constant
                )

            difficulty = chart.difficulty_level

            if difficulty.name.startswith('UTAGE'):
                utage_difficulty = chart.chart_utage_entry.utage_entry_type.name
                difficulty_img_path = UTAGE_DIFF_30PX_PIXMAPS.__getattribute__(utage_difficulty)
            else:
                difficulty_img_path = BASE_DIFF_30PX_PIXMAPS.__getattribute__(difficulty.name)

            if difficulty_img_path is None:
                raise ValueError('Difficulty image not found.')

            chart_creator = None
            if (unquoted_creator_name := TextoutQuotedString.remove_quotes(chart.creator.name_en)):
                chart_creator = unquoted_creator_name
            displays.append(SingleSongDifficultyDisplay(difficulty_img_path, diff_text, chart_creator))

        return displays
