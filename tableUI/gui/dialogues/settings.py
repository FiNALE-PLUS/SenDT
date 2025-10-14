from PySide6.QtCore import Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog, QVBoxLayout, QGroupBox, QFormLayout, QMessageBox
from pydantic import TypeAdapter, ValidationError

from tableUI.gui.widgets.dialogues.completion_buttons import get_dialog_completion_buttons
from tableUI.gui.widgets.form.files.directory_select import DirectorySelectRow
from tableUI.gui.widgets.form.files.validated_path_select import FinaleInstallSelectRow
from tableUI.gui.widgets.settings.backup_settings_flag_panel import BackupFileTypesFlagPanel, BackupFileTypesFlags
from tableUI.gui.widgets.settings.crypt_key_management_panel import CryptKeyManagementPanel
from tableUI.utils.settings.get_settings import get_sendt_settings, write_default_settings_to_default_file, \
    write_settings_to_default_file
from tableUI.utils.settings.models.field_models.paths.game_dir import optionalFinaleInstallDirectory
from tableUI.utils.settings.models.sendt_settings import SenDTSettings


# TODO: Attempt to change values when selected to verify that data is correct

class SenDTSettingsDialog(QDialog):

    def __init__(self, parent=None):
        super(SenDTSettingsDialog, self).__init__(parent)
        self.current_settings = get_sendt_settings()

        screen_size = self.screen().size()
        self.resize(screen_size.width() // 3, screen_size.height() // 4)

        dialog_layout = QVBoxLayout()
        self.setLayout(dialog_layout)

        # Data Directories
        directory_box = QGroupBox('Data Locations')
        dialog_layout.addWidget(directory_box)
        directory_layout = QFormLayout()
        directory_box.setLayout(directory_layout)

        self.data_directory_select = DirectorySelectRow()
        directory_layout.addRow('Custom Data:', self.data_directory_select)
        self.game_directory_select = FinaleInstallSelectRow()
        # self.game_directory_select.pathSelected.connect(self.handleGamePathSelectionChanged)
        directory_layout.addRow('Game Data:', self.game_directory_select)

        # Backup configuration
        backup_settings_box = QGroupBox('Backup Configuration')
        dialog_layout.addWidget(backup_settings_box)
        backup_settings_layout = QVBoxLayout()
        backup_settings_box.setLayout(backup_settings_layout)
        self.backup_file_types_panel = BackupFileTypesFlagPanel()
        backup_settings_layout.addWidget(self.backup_file_types_panel)

        # Encryption keys
        crypt_keys_box = CryptKeyManagementPanel(self.current_settings.keys)
        dialog_layout.addWidget(crypt_keys_box)


        # TODO: Add other settings

        completion_button_components = get_dialog_completion_buttons()
        dialog_layout.addLayout(completion_button_components.layout)
        # TODO: Update and save settings, displaying success dialog once done
        completion_button_components.accept_button.clicked.connect(self.handleAcceptPressed)
        completion_button_components.reject_button.clicked.connect(self.reject)

        self.set_settings_state(self.current_settings)

    def set_settings_state(self, settings: SenDTSettings):
        """
        Updates the settings dialog's components to reflect the values defined in ``settings``.

        :param settings: The settings to base the state of the dialog's widgets on.
        """
        if settings.data.absolute_data_path is not None:
            self.data_directory_select.setCurrentPath(str(settings.data.absolute_data_path))
        if settings.data.default_game_path is not None:
            self.game_directory_select.setCurrentPath(str(settings.data.default_game_path))

        # File type checkboxes
        self.backup_file_types_panel.setFlags(
            BackupFileTypesFlags(
                audio=settings.backup.audio,
                cover_art=settings.backup.cover_art,
                bg_videos=settings.backup.bg_videos,
                charts=settings.backup.charts,
                tables=settings.backup.tables,
            )
        )

    def update_settings_from_dialog(self):
        # Only attempt to overwrite directory settings if one has been actively entered into the line edit
        cur_data_dir = self.data_directory_select.getCurrentPath()
        if cur_data_dir:
            self.current_settings.data.absolute_data_path = cur_data_dir
        cur_game_dir = self.game_directory_select.getCurrentPath()
        if cur_game_dir:
            self.current_settings.data.default_game_path = cur_game_dir

        backup_data_types_requested = self.backup_file_types_panel.getFlags()
        self.current_settings.backup.tables = backup_data_types_requested.tables
        self.current_settings.backup.charts = backup_data_types_requested.charts
        self.current_settings.backup.cover_art = backup_data_types_requested.cover_art
        self.current_settings.backup.bg_videos = backup_data_types_requested.bg_videos
        self.current_settings.backup.audio = backup_data_types_requested.audio

    # @Slot()
    # def handleGamePathSelectionChanged(self):
    #     try:
    #         TypeAdapter(optionalFinaleInstallDirectory).validate_python(self.game_directory_select.getCurrentPath())
    #     except ValidationError as e:
    #         QMessageBox.critical(self, 'Invalid Game Directory',
    #                              f'The game directory could not be validated. Details:'
    #                              # Display the messages of any validation errors raised,
    #                              # without showing part of the stack with it
    #                              f'\n{'\n\n'.join(i['msg'] for i in e.errors())}'
    #                              )

    @Slot()
    def handleAcceptPressed(self):
        try:
            self.update_settings_from_dialog()
            write_settings_to_default_file(self.current_settings)

            success_info = QMessageBox.information(self, 'Settings Saved', 'Settings have been saved successfully.')
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, 'Error Saving Settings',
                                 f'An error occurred while attempting to save settings. Details: \n{str(e)}')

