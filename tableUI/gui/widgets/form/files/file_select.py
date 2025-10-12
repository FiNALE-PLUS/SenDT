from PIL import Image
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QFileDialog, QWidget

exts = Image.registered_extensions()


class FileSelectRow(QHBoxLayout):
    pathSelected = Signal()

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
        self.browse_button.clicked.connect(self._browse_for_expected_path)

    def _browse_for_expected_path(self):
        """
        Wraps the class' ``browse()`` function, ensuring that a signal is
        emitted if a path is chosen and meets its validation standards.
        """
        path = self.browse()

        if path is not None:
            self.pathSelected.emit()

    def get_user_path_selection(self) -> str | None:
        fileName, _ = QFileDialog.getOpenFileName(self.widget(),
                                                  self.dialog_caption,
                                                  self.dir,
                                                  self.filter)

        return fileName

    def browse(self) -> str | None:
        """
        Denotes both the row's query for the user to select a path, and validation to ensure that the path is suitable.
        This should be overridden by subclasses to alder the paths collected and validated, if necessary.

        :return: A string representing the valid selected path if one was chosen, else ``None``.
        """
        fileName = self.get_user_path_selection()
        if fileName:
            self.file_path_entry.setText(fileName)
            return fileName
        return None

    def getCurrentPath(self):
        return self.file_path_entry.text()

    def setCurrentPath(self, path: str):
        self.file_path_entry.setText(path)


class ImageSelectRow(FileSelectRow):
    dialog_caption: str = 'Select Image'
    dir: str = ''
    filter: str = f'Image Files ({' '.join({f"*{ex}" for ex, f in exts.items() if f in Image.OPEN})})'


class VideoSelectRow(FileSelectRow):
    dialog_caption: str = 'Select Video'
    dir: str = ''
    filter: str = (f'Video Files (*.mp4 *.m4v *.mkv *.flv *.f4v *.avi *.wmv *.mov *.webm *.ogv);; '
                   f'All Files (*)')
