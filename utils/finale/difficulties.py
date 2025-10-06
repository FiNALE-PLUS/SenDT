from enum import Enum, unique


@unique
class FinaleChartDifficulty(Enum):
    """
    Represents all possible finale chart difficulties that can be represented in Maimai FiNALE.
    IDs 7-9 and 16+ will crash the game when attempting to be loaded, if included in the relavent tables.
    """
    EASY = 1
    BASIC = 2
    ADVANCED = 3
    EXPERT = 4
    MASTER = 5
    RE_MASTER = 6

    UTAGE_SLOT_1 = 10
    UTAGE_SLOT_2 = 11
    UTAGE_SLOT_3 = 12
    UTAGE_SLOT_4 = 13
    UTAGE_SLOT_5 = 14
    UTAGE_SLOT_6 = 15

    def __str__(self):
        return self.name


@unique
class FinaleUtageType(Enum):
    """
    Includes all Utage chart types within Maimai FiNALE.
    Some types were never used, but are still fully functional within the game
    (those being one-sided, spicy and corner/edge).

    Each type is used as follows [https://silentblue.remywiki.com/maimai:Enkaijou]:


    - *Light:* All notes, including star notes for slide notes and slide notes themselves, are partially or completely changed to Break notes. All touch notes have firework effects enabled.
    - *Star:* Tap notes and break notes are changed to star notes.
    - *Reverse:* Star notes appear at the end of slide notes, instead of the start.
    - *Memorise:* Memorize the order that slide notes appear. All slide notes that previously appeared in a section will appear together, but may not (depending on the song) respond to touches until the previous slide note is gone. The player needs to slide the slide notes in the correct order.
    - *Stroke:* Some slide notes do not come with star notes.
    - *Instant:* The standby time between the star note and slide note is shorter or completely gone.
    - *Tilt:* The original chart is tilted.
    - *Octopus:* More than two simultaneous notes, seemingly requiring more than two hands to play. In reality though, the charts can be played by using arms or elbows.
    - *Co-Op (cooperation):* Playing with multiple players, on the area intended for a single player, is recommended or required. If the chart is a Buddy chart, three or more players will always be required. Due to requiring multiple players, track skip will typically be forced off.
    - *Endure:* A stamina-consuming pattern continuing for most or all of the length of the song, testing the player's endurance. Often combined with forced track skip option.
    - *Banquet:* For charts that don't fit in any other attributes.
    - *Warehourse:* 蔵 refers to お蔵入り, literally "put into the warehouse", that is used to mean scrapped. Charts with this attribute were originally intended for release as normal charts, but were scrapped, often because they're too hard. (Tips on the loading screen added in maimai MiLK revealed that chart designers have to get rank S on non-Utage charts for them to be released.)
    - *Insane:* Crazy difficulty, harder than 宴 or even 蔵 charts.
    - *One-Sided:* Unused in official song lists. The chart forces heavy single-handed movement. This attribute was planned for pre-FiNALE but left unused, so it has its own icon on the official website.
    - *Spicy:* Unused in official song lists. No known use-case, although thought to be similar to banquet.
    - *Corner/Edge:* Unused in official song lists.
    """

    def __init__(self, utage_id: int, kanji: str):
        self.id = utage_id
        self.kanji = kanji

    BANQUET = 1, '宴'
    INSANE = 2, '狂'
    WAREHOUSE = 3, '蔵'
    ENDURE = 4, '耐'
    OCTOPUS = 5, '蛸'
    LIGHT = 6, '光'
    STAR = 7, '星'
    TILT = 8, '傾'
    SPICY = 9, '辛'
    CORNER_OR_EDGE = 10, '角'
    MEMORISE = 11, '覚'
    CO_OP = 12, '協'
    REVERSE = 13, '逆'
    ONE_SIDED = 14, '片'
    INSTANT = 15, '即'
    STROKE = 16, '撫'

    def __str__(self):
        return f'({self.kanji}) {self.name}'

# TODO: Test copies are correct (dict value == enum kanji), add description to enum?
# Maps Utage difficulty IDs to their respective kanji character
# FINALE_UTAGE_TYPE_KANJI: dict[FinaleUtageType, str] = {
#     FinaleUtageType.LIGHT: '光',
#     FinaleUtageType.STAR: '星',
#     FinaleUtageType.REVERSE: '逆',
#     FinaleUtageType.MEMORISE: '覚',
#     FinaleUtageType.STROKE: '撫',
#     FinaleUtageType.INSTANT: '即',
#     FinaleUtageType.TILT: '傾',
#     FinaleUtageType.OCTOPUS: '蛸',
#     FinaleUtageType.CO_OP: '協',
#     FinaleUtageType.ENDURE: '耐',
#     FinaleUtageType.BANQUET: '宴',
#     FinaleUtageType.WAREHOUSE: '蔵',
#     FinaleUtageType.INSANE: '狂',
#     FinaleUtageType.ONE_SIDED: '片',
#     FinaleUtageType.SPICY: '辛',
#     FinaleUtageType.CORNER_OR_EDGE: '角'
# }