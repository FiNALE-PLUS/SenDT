from PIL import Image
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QLabel

from tableUI.const import NO_COVER_IMG
from db.models import Song
from tableUI.gui.dialogues.song_cover_art_preview import \
    SongCoverArtPreviewDialog
from tableUI.paths import get_user_data_cover_art_dir_for


class InteractableSongCoverArtDisplay(QVBoxLayout):
    def __init__(self, song: Song, parent=None):
        super(InteractableSongCoverArtDisplay, self).__init__(parent)

        self.song = song
        # layout = QVBoxLayout()
        # self.setLayout(layout)

        self.cover_art_label = QLabel()
        self.addWidget(self.cover_art_label)
        self.preview_button = QPushButton('Preview Cover Art')
        self.preview_button.clicked.connect(self.show_cover_art_preview)
        self.addWidget(self.preview_button)
        self.setup_widgets()

    def setup_widgets(self):
        expected_cover_art_path = get_user_data_cover_art_dir_for(self.song.id) / 'small.dds'
        if expected_cover_art_path.exists():
            cover_art_img = Image.open(expected_cover_art_path)
        else:
            cover_art_img = NO_COVER_IMG
            self.preview_button.setEnabled(False)
            self.preview_button.setText('No Cover Art')
        self.cover_art_label.setPixmap(cover_art_img.toqpixmap())

    def show_cover_art_preview(self):
        # Using the label as parent target to tie to the display's parent
        preview_dialog = SongCoverArtPreviewDialog(self.song, self.cover_art_label)
        preview_dialog.open()
