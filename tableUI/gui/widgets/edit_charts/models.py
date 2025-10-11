from decimal import Decimal
from typing import NamedTuple

from tableUI.db.models import ChartDifficultyLevel, ChartCreator


class ChartConfigProperties(NamedTuple):
    chart_difficulty_level: ChartDifficultyLevel

    affects_rating: bool
    difficulty_constant: Decimal
    chart_creator: ChartCreator
