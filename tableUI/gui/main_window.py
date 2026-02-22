from pathlib import Path

from PySide6.QtCore import QSize, Slot
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QGroupBox, QHBoxLayout, QFileDialog
from sqlmodel import Session, select

from tableUI.db.models import Chart
from tableUI.gui.actions.export.export_data import export_data
from tableUI.gui.dialogues.convert_chart_data import ChartDataConversionDialog
from tableUI.gui.dialogues.settings import SenDTSettingsDialog
from tableUI.gui.widgets.data_views.song_view import SongTableView, SearchableSongTableView
from tableUI.gui.widgets.data_views.chart import ChartTableView, ChartView


class SenDTuiWindow(QMainWindow):
    def __init__(self, session: Session):
        super().__init__()
        self.db_session = session
        self.setup_toolbar()

        cur_monitor_size = QScreen.availableSize(self.screen())
        self.resize((cur_monitor_size.width() // 4) * 3, (cur_monitor_size.height() // 4) * 3)

        db_chart = session.exec(select(Chart).order_by(Chart.id)).first()
        chart = ChartView(db_chart)

        song_table_layout = QVBoxLayout()

        self.viewer = SearchableSongTableView(self.db_session, modded_only=True)
        self.viewer_layout = QVBoxLayout()
        self.viewer_layout.addWidget(self.viewer)
        self.viewer_box = QGroupBox('Song List')
        self.viewer_box.setLayout(self.viewer_layout)
        song_table_layout.addWidget(self.viewer_box)
        # l.addWidget(QLabel('Charts'))

        centralWidget = QWidget()
        centralWidget.setLayout(song_table_layout)

        self.setCentralWidget(centralWidget)

    def setup_toolbar(self):
        file_menu = self.menuBar().addMenu('&File')

        convert_chart_action = file_menu.addAction('&Convert Chart...')
        convert_chart_action.triggered.connect(self.openChartConverter)

        settings_action = file_menu.addAction('&Settings')
        settings_action.triggered.connect(self.openSettings)

        data_menu = self.menuBar().addMenu('&Data')
        export_action = data_menu.addAction('&Export data to game...')
        export_action.triggered.connect(self.exportData)

    @Slot()
    def openChartConverter(self):
        chart_conversion_dialog = ChartDataConversionDialog(parent=self)

        chart_conversion_dialog.open()

    @Slot()
    def exportData(self):
        selected_dir = QFileDialog.getExistingDirectory(caption='Select a Maimai FiNALE Game Directory')

        if selected_dir:
            export_data(self.db_session, Path(selected_dir), self)

    @Slot()
    def openSettings(self):
        settings_dialog = SenDTSettingsDialog(parent=self)

        settings_dialog.open()