from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .blobs import SdtChartBlob
    from .songs_and_charts import Chart


class UtageType(SQLModel, table=True):
    __tablename__ = 'utage_type'

    id: int                          = Field(primary_key=True)
    name: str                        = Field(nullable=False, unique=True)
    kanji: str                       = Field(nullable=False, unique=True)

    utage_charts: list['UtageEntry'] = Relationship(back_populates='utage_entry_type')


class UtageEntry(SQLModel, table=True):
    __tablename__ = "utage_entry"

    # __table_args__ = (
    #     CheckConstraint(
    #         r"chart_id % 100 BETWEEN 10 AND 15",
    #         name='utage_entry_is_using_utage_chart_slot'
    #     ),
    # )

    id: int | None                   = Field(default=None, primary_key=True)
    event_id: int
    sort_id: int

    chart_id: int                    = Field(foreign_key='chart.id', unique=True, ondelete='CASCADE')
    utage_chart: 'Chart'             = Relationship(back_populates='chart_utage_entry')

    utage_type_id: int               = Field(foreign_key='utage_type.id', ondelete='RESTRICT')
    utage_entry_type: UtageType      = Relationship(back_populates='utage_charts')

    mirror: int
    display: int
    skip: int
    judge: int

    chart_blob_id: int | None        = Field(default=None, foreign_key="sdt_chart_blob.id")
    utage_chart_blob: 'SdtChartBlob' = Relationship(back_populates='blob_utage_charts')
