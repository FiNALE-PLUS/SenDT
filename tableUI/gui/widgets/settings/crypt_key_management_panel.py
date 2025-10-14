from PySide6.QtCore import Slot
from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import QWidget, QGroupBox, QFormLayout, QComboBox, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, \
    QPushButton, QMessageBox
from pydantic import ValidationError

from tableUI.utils.settings.models.crypt_keys import CryptKeySettings



# TODO: Migrate components to separate classes
class CryptKeyManagementPanel(QGroupBox):
    key_value_font = QFont('courier new')
    key_value_font.setStyleHint(QFont.StyleHint.TypeWriter)
    key_value_font.setBold(True)

    def __init__(self, key_settings: CryptKeySettings, parent=None):
        super(CryptKeyManagementPanel, self).__init__(parent)
        self.setTitle('Encryption Keys')
        self.key_settings = key_settings

        existing_key_box = QGroupBox('Existing Keys')
        existing_key_main_layout = QVBoxLayout()
        self.default_existing_key_label = QLabel()
        existing_key_main_layout.addWidget(self.default_existing_key_label)
        existing_key_form = QFormLayout()
        existing_key_main_layout.addLayout(existing_key_form)
        existing_key_box.setLayout(existing_key_main_layout)
        panel_layout = QVBoxLayout()
        self.setLayout(panel_layout)

        # New key addition
        new_key_box = QGroupBox('Add New Key')
        new_key_box_layout = QVBoxLayout()
        new_key_box.setLayout(new_key_box_layout)
        new_key_entries_layout = QFormLayout()
        new_key_box_layout.addLayout(new_key_entries_layout)
        panel_layout.addWidget(new_key_box)
        self.new_key_name_entry = QLineEdit()
        self.new_key_value_entry = QLineEdit()
        new_key_entries_layout.addRow('Name:', self.new_key_name_entry)
        new_key_entries_layout.addRow('Value:', self.new_key_value_entry)
        self.add_new_key_button = QPushButton('Add Key')
        self.add_new_key_button.clicked.connect(self.handleKeyAdded)
        new_key_box_layout.addWidget(self.add_new_key_button)


        # Existing key selection
        panel_layout.addWidget(existing_key_box)

        self.select_key_row = QHBoxLayout()
        self.select_key_widget = QComboBox()
        self.key_value_label = QLabel()
        self.key_value_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.key_value_label.setFont(self.key_value_font)
        self.select_key_row.addWidget(self.select_key_widget)
        self.select_key_row.addWidget(self.key_value_label)
        self.select_key_widget.currentIndexChanged.connect(self.handleSelectedKeyChanged)
        existing_key_form.addRow('Select Existing Key:', self.select_key_row)
        existing_key_action_layout = QHBoxLayout()
        existing_key_main_layout.addLayout(existing_key_action_layout)
        self.set_default_key_button = QPushButton('Set As Default')
        self.set_default_key_button.clicked.connect(self.handleSetKeyDefault)
        self.delete_key_button = QPushButton('Delete Key')
        self.delete_key_button.clicked.connect(self.handleDeleteKey)
        existing_key_action_layout.addWidget(self.set_default_key_button)
        existing_key_action_layout.addWidget(self.delete_key_button)

        self.setup_widgets_from_settings()

    def setup_widgets_from_settings(self):
        self.select_key_widget.clear()
        for key in sorted(self.key_settings.crypt_keys.keys()):
            self.select_key_widget.addItem(key, self.key_settings.crypt_keys[key])
        self.default_existing_key_label.setText(f'Default Key: {self.key_settings.default_key}')

    @Slot()
    def handleKeyAdded(self):
        try:
            self.key_settings.add_key(
                key_name=self.new_key_name_entry.text(),
                key_value=self.new_key_value_entry.text()
            )
            self.setup_widgets_from_settings()
        except KeyError:
            QMessageBox.critical(self, 'Invalid Key Name', f'A key with the name `{self.new_key_name_entry.text()}` already exists. '
                                                           f'Please select a different name, or delete the key using this name.')
        except ValidationError:
            QMessageBox.critical(self, 'Invalid Key Value', 'The given key value is invalid. All keys should be 32 character hex strings.')
        except Exception as e:
            QMessageBox.critical(self, 'Error Adding Key', f'An unknown error has occurred '
                                                           f'when attempting to add a key. Details:\n{e}')

    @Slot()
    def handleSelectedKeyChanged(self):
        if self.select_key_widget.currentData() is not None:
            self.key_value_label.setText(f'{self.select_key_widget.currentData().upper()}')
        else:
            self.key_value_label.setText(f'No key to display.')

    @Slot()
    def handleSetKeyDefault(self):
        try:
            if self.select_key_widget.count() > 0:
                self.key_settings.default_key = self.select_key_widget.currentText()
                self.setup_widgets_from_settings()
            else:
                QMessageBox.warning(self, 'No Keys Available', 'No Keys are available to set as a default. '
                                                               'Please add a key before setting one as the default.')
        except ValidationError as e:
            QMessageBox.critical(self, 'Invalid default key',
                                 'The select default key is invalid. please contact the developer. Details:\n'
                                 f'{e}\n'
                                 f'Crypt Key state:\n'
                                 f'{self.key_settings}')
        except Exception as e:
            QMessageBox.critical(self, 'Error Setting Default Key',
                                 f'An error occured while setting default key. Details:\n{e}')


    def handleDeleteKey(self):
        try:
            response = QMessageBox.question(self, 'Confirm Key Deletion', 'Are you sure you want to delete this key?')
            if response == QMessageBox.StandardButton.Yes:
                if self.key_settings.default_key == self.select_key_widget.currentText():
                    self.key_settings.default_key = None
                self.key_settings.remove_crypt_key_with_name(self.select_key_widget.currentText())
                self.setup_widgets_from_settings()
        except Exception as e:
            QMessageBox.critical(self, 'Error Deleting Key', f'An error occurred while deleting a key. Details:\n{e}')
