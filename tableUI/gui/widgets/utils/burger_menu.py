from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QSizePolicy


class BurgerMenu(QWidget):
    def __init__(self, content: QWidget, expanded: bool = False, parent=None):
        super(BurgerMenu, self).__init__(parent)
        self.content = content

        self.content.setEnabled(expanded)
        self.display_button = QPushButton(self.get_button_text())
        self.display_button.clicked.connect(self.handleExpansion)

        layout = QVBoxLayout(self)
        layout.addWidget(self.display_button)
        layout.addWidget(content)

        self.content.sizePolicy().setRetainSizeWhenHidden(False)

        # self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.setLayout(layout)


    @property
    def expanded(self):
        return self.content.isVisible()


    def handleExpansion(self):
        self.content.setVisible(not self.expanded)

        self.display_button.setText(self.get_button_text())


    def get_button_text(self):
        if self.expanded:
            return u"\u2250"
        else:
            return u"\u2261"

