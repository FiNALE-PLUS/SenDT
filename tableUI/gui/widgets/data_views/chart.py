from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QLabel
from sqlmodel import Session, select

from db.models import Chart
from tableUI.gui.widgets.data_views.fonts import title_font
from tableUI.gui.widgets.utils.burger_menu import BurgerMenu
from tableUI.parsers.tables.field_types.quoted_string import TextoutQuotedString


class ChartView(QWidget):
    def __init__(self, chart: Chart):
        super().__init__()
        self.title = QLabel("Chart")
        self.title.setFont(title_font)
        self.chart = chart

        self.main_layout = QVBoxLayout()

        self.setStyleSheet(
            r"""
            background-color: rgb(60, 60, 60);
            border-radius: 2px;
            border-style: solid;
            border-width: 1px;
            border-color: rgb(100, 100, 100);
            padding: 2px;
            """
        )

        l = QVBoxLayout()
        # header = QHeaderView(Orientation)
        l.addWidget(self.title)
        self.setLayout(l)

    @property
    def chart(self):
        return self._chart

    @chart.setter
    def chart(self, chart: Chart):
        self._chart = chart
        self.update()

    def get_box_name(self) -> str:
        displayed_name = TextoutQuotedString.remove_quotes(self.chart.chart_song.name_en)

        if self.chart.chart_utage_entry:
            difficulty_display = self.chart.chart_utage_entry.utage_entry_type.kanji
        else:
            difficulty_display = self.chart.difficulty_constant
        return (f'{displayed_name} '
                f'- {self.chart.difficulty_level.name} '
                f'({difficulty_display})')

    def update(self):
        self.title.setText(self.get_box_name())


class ChartTableView(QScrollArea):
    def __init__(self, session: Session):
        super().__init__()
        self.db_session = session

        self.internalWidget = QWidget()
        self.internalLayout = QVBoxLayout(self.internalWidget)
        charts = session.exec(select(Chart).order_by(Chart.id)).all()

        for chart in charts:
            self.internalLayout.addWidget(BurgerMenu(ChartView(chart)))

        self.internalWidget.setLayout(self.internalLayout)

        self.setWidget(self.internalWidget)




