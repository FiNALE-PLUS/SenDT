from typing import NamedTuple

from PySide6.QtGui import Qt
from PySide6.QtWidgets import QVBoxLayout, QPushButton, QHBoxLayout, QSizePolicy


class CompletionButtonComponents(NamedTuple):
    accept_button: QPushButton
    reject_button: QPushButton
    layout: QHBoxLayout


def get_dialog_completion_buttons(accept_text: str = 'Accept', reject_text: str = 'Cancel') -> CompletionButtonComponents:
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        # button_layout.setStretch(0, 1)

        accept_button = QPushButton(accept_text)
        accept_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        reject_button = QPushButton(reject_text)
        reject_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        button_layout.addWidget(accept_button)
        button_layout.addWidget(reject_button)

        return CompletionButtonComponents(
            accept_button=accept_button,
            reject_button=reject_button,
            layout=button_layout
        )
