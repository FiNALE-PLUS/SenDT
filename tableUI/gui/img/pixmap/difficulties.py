from doctest import master
from pathlib import Path

from typing_extensions import NamedTuple

from tableUI.const import BASE_DIR
from utils.finale.difficulties import FinaleChartDifficulty

class BaseDifficultyPixmaps(NamedTuple):
    EASY: Path
    BASIC: Path
    ADVANCED: Path
    EXPERT: Path
    MASTER: Path
    RE_MASTER: Path

class UtageDifficultyPixmaps(NamedTuple):
    BANQUET: Path
    INSANE: Path
    WAREHOUSE: Path
    ENDURE: Path
    OCTOPUS: Path
    LIGHT: Path
    STAR: Path
    TILT: Path
    SPICY: Path
    CORNER_OR_EDGE: Path
    MEMORISE: Path
    CO_OP: Path
    REVERSE: Path
    ONE_SIDED: Path
    INSTANT: Path
    STROKE: Path

DIFF_IMG_PATH = BASE_DIR / 'data' / 'img' / 'charts' / 'difficulties'

BASE_DIFF_IMG_PATH = DIFF_IMG_PATH / 'base' / '30'
UTAGE_DIFF_IMG_PATH = DIFF_IMG_PATH / 'utage' / 'kanji_30'

BASE_DIFF_30PX_PIXMAPS = BaseDifficultyPixmaps(
    EASY=Path(BASE_DIFF_IMG_PATH / 'easy.png'),
    BASIC=Path(BASE_DIFF_IMG_PATH / 'basic.png'),
    ADVANCED=Path(BASE_DIFF_IMG_PATH / 'advanced.png'),
    EXPERT=Path(BASE_DIFF_IMG_PATH / 'expert.png'),
    MASTER=Path(BASE_DIFF_IMG_PATH / 'master.png'),
    RE_MASTER=Path(BASE_DIFF_IMG_PATH / 're_master.png')
)

UTAGE_DIFF_30PX_PIXMAPS = UtageDifficultyPixmaps(
    BANQUET=Path(UTAGE_DIFF_IMG_PATH / 'banquet.png'),
    INSANE=Path(UTAGE_DIFF_IMG_PATH / 'insane.png'),
    WAREHOUSE=Path(UTAGE_DIFF_IMG_PATH / 'warehouse.png'),
    ENDURE=Path(UTAGE_DIFF_IMG_PATH / 'endure.png'),
    OCTOPUS=Path(UTAGE_DIFF_IMG_PATH / 'octopus.png'),
    LIGHT=Path(UTAGE_DIFF_IMG_PATH / 'light.png'),
    STAR=Path(UTAGE_DIFF_IMG_PATH / 'star.png'),
    TILT=Path(UTAGE_DIFF_IMG_PATH / 'tilt.png'),
    SPICY=Path(UTAGE_DIFF_IMG_PATH / 'spicy.png'),
    CORNER_OR_EDGE=Path(UTAGE_DIFF_IMG_PATH / 'corner_edge.png'),
    MEMORISE=Path(UTAGE_DIFF_IMG_PATH / 'memorise.png'),
    CO_OP=Path(UTAGE_DIFF_IMG_PATH / 'co_op.png'),
    REVERSE=Path(UTAGE_DIFF_IMG_PATH / 'reverse.png'),
    ONE_SIDED=Path(UTAGE_DIFF_IMG_PATH / 'one_sided.png'),
    INSTANT=Path(UTAGE_DIFF_IMG_PATH / 'instant.png'),
    STROKE=Path(UTAGE_DIFF_IMG_PATH / 'stroke.png')
)
