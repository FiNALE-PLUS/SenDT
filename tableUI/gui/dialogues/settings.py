from PySide6.QtWidgets import QDialog, QVBoxLayout, QGroupBox, QFormLayout

from tableUI.gui.widgets.dialogues.completion_buttons import get_dialog_completion_buttons
from tableUI.gui.widgets.form.files.directory_select import DirectorySelectRow
from tableUI.utils.settings.get_settings import get_sendt_settings


# TODO: Attempt to change values when selected to verify that data is correct

class SenDTSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SenDTSettingsDialog, self).__init__(parent)
        self.current_settings = get_sendt_settings()

        dialog_layout = QVBoxLayout()
        self.setLayout(dialog_layout)

        # Data Directories
        directory_box = QGroupBox('Data Locations')
        dialog_layout.addWidget(directory_box)
        directory_layout = QFormLayout()
        directory_box.setLayout(directory_layout)

        self.data_directory_select = DirectorySelectRow()
        directory_layout.addRow('Custom Data:', self.data_directory_select)

        completion_button_components = get_dialog_completion_buttons()
        dialog_layout.addLayout(completion_button_components.layout)
        # TODO
        completion_button_components.accept_button.clicked.connect(self.handleAcceptPressed)
        completion_button_components.reject_button.clicked.connect(self.reject)


    def handleAcceptPressed(self):
        print(self.current_settings)
        self.accept()

