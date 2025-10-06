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
from tableUI.parsers.tables.field_types.quoted_string import TextoutQuotedString


class ChartConfigProperties(NamedTuple):
    chart_difficulty_level: ChartDifficultyLevel

    affects_rating: bool
    difficulty_constant: Decimal
    chart_creator: ChartCreator


class SingleBaseChartConfigurationPanel(QFrame):

    chart_level_title_font = QFont()
    chart_level_title_font.setPointSize(12)

    def __init__(self, session: Session, chart: Chart, parent=None):
        super(SingleBaseChartConfigurationPanel, self).__init__(parent)
        self.chart = chart
        self.db_session = session
        self.setObjectName('SingleBaseChartConfigurationPanel')
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.setStyleSheet(
            get_outlined_frame_stylesheet(self.objectName())
        )
        title = QLabel(self.chart.difficulty_level.name)
        title.setFont(self.chart_level_title_font)
        layout.addWidget(title)

        chart_options_layout = QFormLayout()
        layout.addLayout(chart_options_layout)
        self.affects_rating_select = QCheckBox()
        chart_options_layout.addRow('Affects Rating', self.affects_rating_select)

        self.difficulty_constant_select = QDoubleSpinBox()
        self.difficulty_constant_select.setMinimum(0)
        self.difficulty_constant_select.setMaximum(14)
        self.difficulty_constant_select.setSingleStep(0.1)
        self.difficulty_constant_select.setDecimals(1)
        chart_options_layout.addRow('Difficulty Constant:', self.difficulty_constant_select)

        self.chart_creator_select = QComboBox()
        chart_options_layout.addRow('Chart Creator:', self.chart_creator_select)
        # layout.addWidget(QLabel(str(self.chart)))
        self.fill_options_from_chart_data()

    @property
    def chart_form_props(self):
        # filled_chart = self.chart
        # filled_chart.song_id = self.chart.chart_song.id
        # filled_chart.affects_rating = self.affects_rating_select.isChecked()
        #
        # diff_constant = self.difficulty_constant_select.text()
        # filled_chart.difficulty_constant = Decimal(diff_constant)
        # filled_chart.creator = self.chart_creator_select.currentData()

        self.chart.affects_rating = self.affects_rating_select.isChecked()
        self.chart.difficulty_constant = Decimal(self.difficulty_constant_select.text())
        self.chart.creator = self.chart_creator_select.currentData()

        return self.chart


        # return ChartConfigProperties(
        #     chart_difficulty_level=self.chart.difficulty_level,
        #
        #     affects_rating=self.affects_rating_select.isChecked(),
        #     difficulty_constant=Decimal(self.difficulty_constant_select.text()),
        #     chart_creator=self.chart_creator_select.currentData(),
        # )

    def fill_options_from_chart_data(self):
        self.affects_rating_select.setChecked(self.chart.affects_rating)
        self.difficulty_constant_select.setValue(float(self.chart.difficulty_constant))

        chart_creators = self.db_session.exec(
            select(ChartCreator).order_by(ChartCreator.name_en)
        ).all()

        self.chart_creator_select.clear()
        for creator in chart_creators:
            self.chart_creator_select.addItem(TextoutQuotedString.remove_quotes(creator.name_en), creator)

        if self.chart.creator is not None:
            self.chart_creator_select.setCurrentIndex(self.chart_creator_select.findData(self.chart.creator))


class SongBaseChartConfigurationPanel(QWidget):

    def __init__(self, session: Session, song: Song, parent=None):
        super(SongBaseChartConfigurationPanel, self).__init__(parent)
        self.song = song
        self.db_session = session

        self.base_chart_config_panels: list[SingleBaseChartConfigurationPanel] = []

        base_chart_layout = QVBoxLayout()

        charts = session.exec(
            select(Chart).where(Chart.chart_song == song).order_by(Chart.difficulty_level_id)
        ).all()

        for chart in charts:
            if chart.chart_utage_entry is None:
                panel = SingleBaseChartConfigurationPanel(self.db_session, chart)
                self.base_chart_config_panels.append(panel)
                base_chart_layout.addWidget(panel)

        self.setLayout(base_chart_layout)

    def getBaseChartConfigurations(self) -> List[Chart]:
        configs = []
        for panel in self.base_chart_config_panels:
            configs.append(panel.chart_form_props)
        return configs


class UtageChartPanel(SingleBaseChartConfigurationPanel):
    ...


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


