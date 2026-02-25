import os
from decimal import Decimal

from PySide6.QtCore import Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QFormLayout, QCheckBox, QDoubleSpinBox, QComboBox, \
    QHBoxLayout, QPushButton, QMessageBox
from sqlmodel import Session, select

from tableUI.const import BASE_DIR
from tableUI.db.models import Chart, ChartCreator
from tableUI.gui.dialogues.convert_chart_data import ChartDataConversionDialog
from tableUI.gui.stylesheets.frame import get_outlined_frame_stylesheet
from tableUI.parsers.tables.field_types.quoted_string import TextoutQuotedString
from tableUI.utils.paths.internal_data_paths import get_internal_chart_path


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

        chart_file_action_layout = QHBoxLayout()
        layout.addLayout(chart_file_action_layout)
        self.update_chart_file_button = QPushButton('Update Chart File...')
        self.update_chart_file_button.clicked.connect(self.updateChartFile)
        self.delete_chart_file_button = QPushButton()
        self.delete_chart_file_button.clicked.connect(self.deleteChartFile)
        chart_file_action_layout.addWidget(self.update_chart_file_button)
        chart_file_action_layout.addWidget(self.delete_chart_file_button)

        self.update_layout_from_data_state()
        self.fill_options_from_chart_data()

    @Slot()
    def updateChartFile(self):
        conversion_dialog = ChartDataConversionDialog(self, self.chart)
        conversion_dialog.exec()

        self.update_layout_from_data_state()

    @Slot()
    def deleteChartFile(self):
        try:
            os.remove(get_internal_chart_path(self.chart))
            QMessageBox.information(self, 'Chart File Deleted', 'The chart file has been successfully deleted.')
        except PermissionError:
            QMessageBox.critical(self, 'Permission Error', 'Permission has been denied to the file. '
                                                           'Does another program currently have it open?')
        except FileNotFoundError:
            pass
        except Exception as e:
            QMessageBox.critical(self, 'Error',
                                 f'An error occurred while trying to delete the chart file. '
                                 f'(Details: {type(e)} - {str(e)})')
        finally:
            self.update_layout_from_data_state()

    def update_layout_from_data_state(self):
        chart_available = self.checkChartFileAvailablity()

        if chart_available:
            self.delete_chart_file_button.setText('Delete Current Chart File')
            self.delete_chart_file_button.setEnabled(True)
        else:
            self.delete_chart_file_button.setText('No Chart to Delete')
            self.delete_chart_file_button.setEnabled(False)

    def checkChartFileAvailablity(self):
        expected_path = get_internal_chart_path(self.chart)

        return expected_path.is_file()

    @property
    def chart_form_props(self):
        self.chart.affects_rating = self.affects_rating_select.isChecked()
        self.chart.difficulty_constant = Decimal(self.difficulty_constant_select.text())
        self.chart.creator = self.chart_creator_select.currentData()

        return self.chart

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
