from abc import ABC, abstractmethod, ABCMeta

from PySide6.QtWidgets import QMessageBox
from pydantic import BaseModel, TypeAdapter, ValidationError

from tableUI.gui.widgets.form.files.directory_select import DirectorySelectRow
from tableUI.utils.settings.models.field_models.paths.game_dir import optionalFinaleInstallDirectory


class ValidatedDirectorySelectRow(DirectorySelectRow):

    error_dialogue_title = 'Invalid Path'
    error_dialogue_summary = 'The selected path failed validation.'

    @classmethod
    @property
    def path_validation_model(cls) -> type[BaseModel]:
        raise NotImplementedError
        return BaseModel

    @classmethod
    def validate_input_data(cls, path: str):
        TypeAdapter(cls.path_validation_model).validate_python(path)

    def setCurrentPath(self, path: str):
        """
        Enforces validation of the path before setting, guaranteeing that path values
        set programmatically are subject to the same validation as those set by the user.
        """
        self.validate_input_data(path)
        super().setCurrentPath(path)

    def __init__(self, parent=None):
        DirectorySelectRow.__init__(self, parent)

    def get_user_path_selection(self) -> str | None:
        selected_path = super().get_user_path_selection()

        if selected_path == '':
            return None

        try:
            self.validate_input_data(selected_path)
            return selected_path
        except ValidationError as e:
            # use file line edit as connection to parent window
            QMessageBox.critical(self.file_path_entry, self.error_dialogue_title,
                                 f'{self.error_dialogue_summary} Details:'
                                 # Display the messages of any validation errors raised, 
                                 # without showing part of the stack with it
                                 f'\n{'\n\n'.join(i['msg'] for i in e.errors())}'
                                 )
        except Exception as e:
            QMessageBox.critical(self.file_path_entry, self.error_dialogue_title,
                                 f'An unknown error occurred when validating the selected path. Details:\n{e}')


class FinaleInstallSelectRow(ValidatedDirectorySelectRow):
    error_dialogue_title = 'Invalid Game Directory'
    error_dialogue_summary = 'The selected game directory could not be verified to be a valid installation of the game.'

    @classmethod
    @property
    def path_validation_model(cls) -> type[BaseModel]:
        return optionalFinaleInstallDirectory
