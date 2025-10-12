from PySide6.QtWidgets import QFileDialog

from tableUI.gui.widgets.form.files.file_select import FileSelectRow


class DirectorySelectRow(FileSelectRow):

    def __init__(self, parent=None):
        super(DirectorySelectRow, self).__init__(parent)

        self.browse_button.setText("Select Folder...")

    def browse(self):
        dirName = QFileDialog.getExistingDirectory(self.widget(), "Select Folder...")
        if dirName:
            self.file_path_entry.setText(dirName)