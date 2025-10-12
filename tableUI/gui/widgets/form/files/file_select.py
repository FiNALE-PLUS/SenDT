from PIL import Image
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QFileDialog, QWidget

exts = Image.registered_extensions()

class FileSelectRow(QHBoxLayout):
    dialog_caption: str = 'Select File'
    dir: str = ''
    filter: str = 'All Files (*)'

    def __init__(self, parent=None):
        super(FileSelectRow, self).__init__(parent)

        self.file_path_entry = QLineEdit()
        self.file_path_entry.setReadOnly(True)
        self.browse_button = QPushButton('Select File...')

        self.addWidget(self.file_path_entry)
        self.addWidget(self.browse_button)
        self.browse_button.clicked.connect(self.browse)

    def browse(self):
        fileName, filter = QFileDialog.getOpenFileName(self.widget(),
                                                       self.dialog_caption,
                                                       self.dir,
                                                       self.filter)
        if fileName:
            self.file_path_entry.setText(fileName)

    def getFilePath(self):
        return self.file_path_entry.text()


class ImageSelectRow(FileSelectRow):
    dialog_caption: str = 'Select Image'
    dir: str = ''
    filter: str = f'Image Files ({' '.join({f"*{ex}" for ex, f in exts.items() if f in Image.OPEN})})'


class VideoSelectRow(FileSelectRow):
    dialog_caption: str = 'Select Video'
    dir: str = ''
    filter: str = (f'Video Files (*.mp4 *.m4v *.mkv *.flv *.f4v *.avi *.wmv *.mov *.webm *.ogv);; '
                   f'All Files (*)')
