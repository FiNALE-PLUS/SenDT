from typing import NamedTuple

from PySide6.QtGui import Qt
from PySide6.QtWidgets import QVBoxLayout, QPushButton, QHBoxLayout


class CompletionButtonComponents(NamedTuple):
    accept_button: QPushButton
    reject_button: QPushButton
    layout: QHBoxLayout


def get_dialog_completion_buttons(accept_text: str = 'Accept', reject_text: str = 'Cancel') -> CompletionButtonComponents:
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        accept_button = QPushButton(accept_text)
        reject_button = QPushButton(reject_text)

        button_layout.addWidget(accept_button)
        button_layout.addWidget(reject_button)

        return CompletionButtonComponents(
            accept_button=accept_button,
            reject_button=reject_button,
            layout=button_layout
        )
