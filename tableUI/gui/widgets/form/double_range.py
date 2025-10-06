from typing import NamedTuple

from PySide6.QtCore import Slot
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QDoubleSpinBox, QVBoxLayout, QHBoxLayout


class RangeBounds(NamedTuple):
    lower_bound: float
    upper_bound: float


class DoubleRangeSpinBoxes(QHBoxLayout):
    def __init__(self, parent=None):
        super(DoubleRangeSpinBoxes, self).__init__(parent)

        self.lower_bound_spinbox = QDoubleSpinBox()
        self.upper_bound_spinbox = QDoubleSpinBox()
        self.lower_bound_spinbox.valueChanged.connect(self.handle_lower_bound_change)
        self.upper_bound_spinbox.valueChanged.connect(self.handle_upper_bound_change)

        # layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.addWidget(self.lower_bound_spinbox)
        self.addWidget(self.upper_bound_spinbox)
        # self.setLayout(layout)

    @Slot(float)
    def handle_lower_bound_change(self, value):
        if value > self.upper_bound_spinbox.value():
            self.upper_bound_spinbox.setValue(value)

    @Slot(float)
    def handle_upper_bound_change(self, value):
        if value < self.lower_bound_spinbox.value():
            self.lower_bound_spinbox.setValue(value)

    def getRange(self):
        return RangeBounds(lower_bound=self.lower_bound_spinbox.value(),
                           upper_bound=self.upper_bound_spinbox.value())

    def getLowerBound(self):
        return self.lower_bound_spinbox.value()

    def getUpperBound(self):
        return self.upper_bound_spinbox.value()

    def setLowerBound(self, value):
        self.lower_bound_spinbox.setValue(value)

    def setUpperBound(self, value):
        self.upper_bound_spinbox.setValue(value)

    def setMutualMinimum(self, value):
        self.lower_bound_spinbox.setMinimum(value)
        self.upper_bound_spinbox.setMinimum(value)

    def setMutualMaximum(self, value):
        self.lower_bound_spinbox.setMaximum(value)
        self.upper_bound_spinbox.setMaximum(value)

    def setSingleStep(self, step):
        self.lower_bound_spinbox.setSingleStep(step)
        self.upper_bound_spinbox.setSingleStep(step)