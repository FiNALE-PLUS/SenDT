from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog, QVBoxLayout, QGroupBox, QFormLayout, QMessageBox
from pydantic import TypeAdapter, ValidationError

from tableUI.gui.widgets.dialogues.completion_buttons import get_dialog_completion_buttons
from tableUI.gui.widgets.form.files.directory_select import DirectorySelectRow
from tableUI.utils.settings.get_settings import get_sendt_settings
from tableUI.utils.settings.models.field_models.paths.game_dir import optionalFinaleInstallDirectory


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
        self.game_directory_select = DirectorySelectRow()
        self.game_directory_select.pathSelected.connect(self.handleGamePathSelectionChanged)
        directory_layout.addRow('Game Data:', self.game_directory_select)

        completion_button_components = get_dialog_completion_buttons()
        dialog_layout.addLayout(completion_button_components.layout)
        # TODO
        completion_button_components.accept_button.clicked.connect(self.handleAcceptPressed)
        completion_button_components.reject_button.clicked.connect(self.reject)

    @Slot()
    def handleGamePathSelectionChanged(self):
        try:
            TypeAdapter(optionalFinaleInstallDirectory).validate_python(self.game_directory_select.getCurrentPath())
        except ValidationError as e:
            QMessageBox.critical(self, 'Invalid Game Directory',
                                 f'The game directory could not be validated. Details:'
                                 # Display the messages of any validation errors raised, 
                                 # without showing part of the stack with it
                                 f'\n{'\n\n'.join(i['msg'] for i in e.errors())}'
                                 )

    @Slot()
    def handleAcceptPressed(self):

        self.current_settings.data.absolute_data_path = self.data_directory_select.getFilePath()
        print(self.current_settings)

        self.accept()

