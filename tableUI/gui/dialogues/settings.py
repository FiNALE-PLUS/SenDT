from PySide6.QtWidgets import QDialog, QVBoxLayout


class SenDTSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SenDTSettingsDialog, self).__init__(parent)

        dialog_layout = QVBoxLayout()

