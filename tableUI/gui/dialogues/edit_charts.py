from decimal import Decimal
from math import isclose
from typing import List, Collection, Any, NamedTuple

from PySide6.QtCore import Signal
from PySide6.QtGui import Qt, QFont
from PySide6.QtWidgets import QDialog, QFrame, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QTabWidget, QWidget, \
    QFormLayout, QCheckBox, QDoubleSpinBox, QComboBox
from sqlmodel import Session, select

from tableUI.db.models import Song, Chart, ChartCreator, ChartDifficultyLevel
from tableUI.gui.stylesheets.frame import get_outlined_frame_stylesheet, get_highlight_outlined_frame_stylesheet, \
    get_tab_highlight_outlined_frame_stylesheet
from tableUI.gui.widgets.edit_charts.models import ChartConfigProperties
from tableUI.gui.widgets.edit_charts.panels.base_chart import SingleBaseChartConfigurationPanel, \
    SongBaseChartConfigurationPanel
from tableUI.parsers.tables.field_types.quoted_string import TextoutQuotedString

class ChartReconfigurationArgs(NamedTuple):
    song: Song

    chart_props: list[ChartConfigProperties]


class ChartManagementDialog(QDialog):

    # TODO: Emits list[Chart], but that type cannot be used correctly
    chartConfigurationComplete = Signal(ChartReconfigurationArgs)

    def __init__(self, session: Session, song: Song | None, parent=None):
        super(ChartManagementDialog, self).__init__(parent)
        self.db_session = session
        self.song = song
        self.setWindowTitle(f'Edit Charts - {TextoutQuotedString.remove_quotes(self.song.name_en)}')

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.base_chart_config_widget = SongBaseChartConfigurationPanel(self.db_session, self.song)
        self.tabs.addTab(self.base_chart_config_widget, '&Base Charts')

        # Accept & Reject buttons
        self.buttonBox = QHBoxLayout()
        self.buttonBox.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.add_completion_buttons_to_button_box()
        main_layout.addLayout(self.buttonBox)

    def fillChartsFromForm(self):
        base_chart_configurations = self.base_chart_config_widget.getBaseChartConfigurations()

        # TODO: Explicitly select and update properties within charts,
        #  as opposed to attempting to pass models back and forth

        # for chart in base_charts:
        #     print(chart.song_id, chart.chart_song)

        self.chartConfigurationComplete.emit(
            base_chart_configurations
        )
        self.accept()

    def handleAcceptPressed(self):
        self.fillChartsFromForm()

    def add_completion_buttons_to_button_box(self):
        accept_button = QPushButton("Accept")
        accept_button.clicked.connect(self.handleAcceptPressed)
        reject_button = QPushButton("Cancel")
        reject_button.clicked.connect(self.reject)
        self.buttonBox.addStretch()
        self.buttonBox.addWidget(accept_button)
        self.buttonBox.addWidget(reject_button)


