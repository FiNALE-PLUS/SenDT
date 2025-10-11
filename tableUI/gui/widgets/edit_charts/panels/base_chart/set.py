from typing import List

from PySide6.QtWidgets import QWidget, QVBoxLayout
from sqlmodel import Session, select

from tableUI.db.models import Song, Chart
from tableUI.gui.widgets.edit_charts.panels.base_chart.single import SingleBaseChartConfigurationPanel


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