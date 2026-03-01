from PIL.Image import Image as PILImage
from PySide6.QtGui import Qt, QPalette, QColor
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QGroupBox, QVBoxLayout

from db.models import Song
from tableUI.utils.assets.song_cover.dds.read import open_cover_art_images_for_song_id
from tableUI.parsers.tables.field_types.quoted_string import TextoutQuotedString


def build_groupboxed_image(image: PILImage, title: str) -> QGroupBox:
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    image_label = QLabel()
    image_label.setPixmap(image.toqpixmap())
    layout.addWidget(image_label)
    group_box = QGroupBox(title)
    group_box.setLayout(layout)
    return group_box



class SongCoverArtPreviewDialog(QDialog):

    def __init__(self, song: Song, parent=None):
        super(SongCoverArtPreviewDialog, self).__init__(parent=parent)
        self.song = song
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(132, 154, 206))
        self.setPalette(palette)
        self.setWindowTitle(f'Cover Art Preview - {TextoutQuotedString.remove_quotes(self.song.name_en)}')

        large_img_layout = QHBoxLayout()
        large_img_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        small_img_layout = QHBoxLayout()
        small_img_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout = QVBoxLayout()
        main_layout.addLayout(large_img_layout)
        main_layout.addLayout(small_img_layout)
        self.setLayout(main_layout)

        # TODO
        cover_images = open_cover_art_images_for_song_id(self.song.id)

        large_img_layout.addStretch()
        # full_size_groupbox = build_groupboxed_image(cover_images.full_size, 'Full Size')
        full_size_label = QLabel()
        full_size_label.setPixmap(cover_images.full_size.toqpixmap())
        large_img_layout.addWidget(full_size_label)
        large_img_layout.addStretch()
        # mirror_groupbox = build_groupboxed_image(cover_images.mirror_effect, 'Mirror Effect (Top Screen)')
        mirror_label = QLabel()
        mirror_label.setPixmap(cover_images.mirror_effect.toqpixmap())
        large_img_layout.addWidget(mirror_label)
        large_img_layout.addStretch()
        # large_img_layout.addWidget(mirror_groupbox)

        # small_groupbox = build_groupboxed_image(cover_images.small, 'Small')
        small_label = QLabel()
        small_label.setPixmap(cover_images.small.toqpixmap())
        small_img_layout.addStretch()
        small_img_layout.addWidget(small_label)
        small_img_layout.addStretch()

        # self.setMaximumSize(self.size())
