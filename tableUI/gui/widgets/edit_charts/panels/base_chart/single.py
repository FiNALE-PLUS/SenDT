from decimal import Decimal

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QFormLayout, QCheckBox, QDoubleSpinBox, QComboBox
from sqlmodel import Session, select

from tableUI.db.models import Chart, ChartCreator
from tableUI.gui.stylesheets.frame import get_outlined_frame_stylesheet
from tableUI.parsers.tables.field_types.quoted_string import TextoutQuotedString


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