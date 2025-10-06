from PySide6.QtCore import Slot
from PySide6.QtWidgets import QGroupBox, QLineEdit, QFormLayout


class GroupBoxedLangEntries(QGroupBox):
    """
    Creates a form to enter an english and japanese string, surrounded by a group box.
    """

    def __init__(self, title: str, parent=None):
        super().__init__(title=title, parent=parent)

        self.eng_entry = QLineEdit()
        self.jp_entry = QLineEdit()

        layout = QFormLayout()
        layout.addRow("English:", self.eng_entry)
        layout.addRow("Japanese:", self.jp_entry)

        self.setLayout(layout)

    def getEnglish(self):
        return self.eng_entry.text()

    def setEnglish(self, eng: str):
        self.eng_entry.setText(eng)

    def getJapanese(self):
        return self.jp_entry.text()

    def setJapanese(self, jp: str):
        self.jp_entry.setText(jp)


class GroupBoxedTextoutLangEntries(GroupBoxedLangEntries):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)

        self.eng_entry.textEdited.connect(self.filterEnglish)
        self.jp_entry.textEdited.connect(self.filterJapanese)

    @Slot(str)
    def filterInvalidCharacters(self, text: str) -> str:
        return text.replace('"', '')

    def filterEnglish(self):
        self.setEnglish(self.filterInvalidCharacters(self.getEnglish()))

    def filterJapanese(self):
        self.setJapanese(self.filterInvalidCharacters(self.getJapanese()))
