from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QGroupBox, QFormLayout, QComboBox, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit

from tableUI.utils.settings.models.crypt_keys import CryptKeySettings


class CryptKeyManagementPanel(QGroupBox):

    def __init__(self, key_settings: CryptKeySettings, parent=None):
        super(CryptKeyManagementPanel, self).__init__(parent)
        self.setTitle('Encryption Keys')
        self.key_settings = key_settings

        existing_key_box = QGroupBox('Existing Keys')
        existing_key_layout = QFormLayout()
        existing_key_box.setLayout(existing_key_layout)
        panel_layout = QVBoxLayout()
        self.setLayout(panel_layout)

        # New key addition
        new_key_box = QGroupBox('Add New Key')
        new_key_layout = QFormLayout()
        new_key_box.setLayout(new_key_layout)
        panel_layout.addWidget(new_key_box)
        self.new_key_name_entry = QLineEdit()
        self.new_key_value_entry = QLineEdit()

        # Existing key selection
        panel_layout.addWidget(existing_key_box)

        self.select_key_row = QHBoxLayout()
        self.select_key_widget = QComboBox()
        self.key_value_label = QLabel()
        self.select_key_row.addWidget(self.select_key_widget)
        self.select_key_row.addWidget(self.key_value_label)
        self.select_key_widget.currentIndexChanged.connect(self.handleSelectedKeyChanged)
        existing_key_layout.addRow('Select Existing Key:', self.select_key_row)

        self.setup_widgets_from_settings()

    def setup_widgets_from_settings(self):
        self.select_key_widget.clear()
        for key in sorted(self.key_settings.crypt_keys.keys()):
            self.select_key_widget.addItem(key, self.key_settings.crypt_keys[key])



    @Slot()
    def handleSelectedKeyChanged(self):
        self.key_value_label.setText(f'Value: {self.select_key_widget.currentData().upper()}')
