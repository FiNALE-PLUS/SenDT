from PySide6.QtWidgets import QFileDialog

from tableUI.gui.widgets.form.files.file_select import FileSelectRow


class DirectorySelectRow(FileSelectRow):

    def __init__(self, parent=None):
        super(DirectorySelectRow, self).__init__(parent)

        self.browse_button.setText("Select Folder...")

    def get_user_path_selection(self) -> str | None:
        dirName = QFileDialog.getExistingDirectory(self.widget(), "Select Folder...")
        return dirName
