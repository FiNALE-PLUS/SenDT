import os

from PySide6.QtWidgets import QPushButton

from tableUI.db.models import Song
from tableUI.gui.widgets.data_views.song_view.components.cong_cover_art_view import InteractableSongCoverArtDisplay
from tableUI.utils.paths.internal_data_paths import get_internal_bg_video_path_for_song_id


class CoverArtDisplayWithBGVideoPreview(InteractableSongCoverArtDisplay):
    def __init__(self, song: Song, parent=None):
        super().__init__(song, parent)

        self.bg_video_preview_button = QPushButton('Preview BG Video')
        self.addWidget(self.bg_video_preview_button)

        self.setup_bg_preview_button()

    def setup_bg_preview_button(self):
        bg_video_path = get_internal_bg_video_path_for_song_id(self.song.id)

        if not bg_video_path.exists():
            self.bg_video_preview_button.setEnabled(False)
            self.bg_video_preview_button.setText('No BG Video')
        else:
            self.bg_video_preview_button.clicked.connect(self.preview_bg_video)

    def preview_bg_video(self):
        """
        Opens the current BG video for the song in the OS's current default video player.
        """
        os.startfile(get_internal_bg_video_path_for_song_id(self.song.id))
