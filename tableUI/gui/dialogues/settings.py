from PySide6.QtWidgets import QDialog, QVBoxLayout

from tableUI.utils.settings.get_settings import get_sendt_settings


# TODO: Attempt to change values when selected to verify that data is correct

class SenDTSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SenDTSettingsDialog, self).__init__(parent)
        self.current_settings = get_sendt_settings()

        dialog_layout = QVBoxLayout()

