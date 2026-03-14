from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .songs_and_charts import Chart
    from .utage import UtageEntry


class SdtChartBlob(SQLModel, table=True):
    __tablename__ = 'sdt_chart_blob'

    id: int | None                        = Field(primary_key=True)

    chart: str                            = Field(nullable=False,
                                            # Valid if the whole file content matches the pattern

                                            # TODO: Add conditional to ban non-zero slide ID with slide pattern of zero?
                                            regex=r'(?:(?P<whole_measure>\d+.\d{4}),\s*'
                                                    r'(?P<fractional_measure>\d+.\d{4}),\s*'
                                                    r'(?P<duration>\d+.\d{4}),\s*'
                                                    r'(?P<location>[01234567]),\s*'
                                                    r'(?P<type>128|0|1|2|3|4|5),\s*'
                                                    r'(?P<slide_id>\d+),\s*'
                                                    r'(?P<slide_pattern>10|11|12|13|0|1|2|3|4|5|6|7|8|9),\s*'  # 0 only used for non-slides
                                                    r'(?P<slide_count>\d+),\s*'
                                                    r'(?P<slide_delay>\d+.\d{4}),\n*)+')  # repeat for as many lines as the file requires

    blob_base_charts: list['Chart']       = Relationship(back_populates="base_chart_blob")
    blob_utage_charts: list['UtageEntry'] = Relationship(back_populates="utage_chart_blob")
    
    
class VideoBlob(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    data: bytes = Field(nullable=False)