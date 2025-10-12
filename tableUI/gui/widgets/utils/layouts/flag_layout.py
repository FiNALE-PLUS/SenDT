from PySide6.QtWidgets import QGridLayout, QCheckBox


def get_checkbox_grid_layout(checkboxes_per_row: int, *checkboxes: QCheckBox) -> QGridLayout:
    checkbox_layout = QGridLayout()

    for i, checkbox in enumerate(checkboxes):
        checkbox_layout.addWidget(checkbox, i // checkboxes_per_row, i % checkboxes_per_row)

    return checkbox_layout
