from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

from tableUI.gui.widgets.data_views.fonts import title_font, subtitle_font


class TitleWidget(QWidget):
    def __init__(self, title: str, subtitle: str | None = None,
                 max_title_length: int = 35, max_subtitle_length: int = 40, parent=None):
        super(TitleWidget, self).__init__(parent)
        self.max_title_length = max_title_length
        self.max_subtitle_length = max_subtitle_length

        self.title = QLabel()
        self.title_text = title
        self.title.setFont(title_font)
        self.subtitle = QLabel()
        self.subtitle.setFont(subtitle_font)

        if subtitle is not None:
            self.subtitle_text = subtitle
        else:
            self.subtitle.setVisible(False)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.subtitle)

        self.setLayout(self.layout)

    def get_truncated_string(self, text: str, max_length: int):
        return text if len(text) <= max_length else f'{text[:max_length - 3]}...'

    @property
    def title_text(self):
        return self._title_text

    @title_text.setter
    def title_text(self, title: str):
        self._title_text = title
        self.title.setText(self.get_truncated_string(self._title_text, self.max_title_length))

    @property
    def subtitle_text(self):
        return self._subtitle_text

    @subtitle_text.setter
    def subtitle_text(self, subtitle: str):
        self._subtitle_text = subtitle
        self.subtitle.setText(self.get_truncated_string(self._subtitle_text, self.max_title_length))


class FinaleSongTitleWidget(TitleWidget):

    safename_font = QFont('courier new')
    safename_font.setBold(True)

    def __init__(self, title: str, artist: str, safename: str,
                 max_title_length: int = 35, max_subtitle_length: int = 40, parent=None):
        super().__init__(title, artist, max_title_length, max_subtitle_length, parent)

        self.safename_label = QLabel()
        self.safename_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.safename_label.setFont(title_font)
        self.safename_label.setFont(self.safename_font)
        self.safename_text = safename

        self.layout.addWidget(self.safename_label)

    @property
    def safename_text(self):
        return self._safename_text

    @safename_text.setter
    def safename_text(self, safename: str):
        self._safename_text = safename
        self.safename_label.setText(safename)