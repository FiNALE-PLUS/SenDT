from typing import NamedTuple

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTabWidget
from sqlmodel import Session

from db.models import Song
from tableUI.gui.widgets.dialogues.completion_buttons import get_dialog_completion_buttons
from tableUI.gui.widgets.edit_charts.models import ChartConfigProperties
from tableUI.gui.widgets.edit_charts.panels.base_chart import SongBaseChartConfigurationPanel
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
        completion_button_components = get_dialog_completion_buttons()
        self.completionButtonLayout = completion_button_components.layout
        completion_button_components.accept_button.clicked.connect(self.handleAcceptPressed)
        completion_button_components.reject_button.clicked.connect(self.reject)
        main_layout.addLayout(self.completionButtonLayout)

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


