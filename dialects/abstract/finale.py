import math
import pprint
import re
import warnings
from collections import namedtuple
from enum import Enum
from typing import TypedDict, NamedTuple


class SDTNoteType(Enum):
    START_SLIDE = 0
    TAP = 1
    HOLD = 2
    BREAK = 3
    SLIDE_STAR = 4
    SLIDE_STAR_BREAK = 5
    END_SLIDE = 128


class SDTSlidePattern(Enum):
    STRAIGHT_LINE = 1
    OUTER_CIRCLE_CCW = 2
    OUTER_CIRCLE_CW = 3
    INNER_ARC_CCW = 4
    INNER_ARC_CW = 5
    ZIGZAG_S = 6
    ZIGZAG_Z = 7
    V_CENTER_END = 8
    STRAIGHT_CENTER_ARC_CCW = 9
    STRAIGHT_CENTER_ARC_CW = 10
    START_CCW_TWO_END = 11
    START_CW_TWO_END = 12
    FAN = 13


class SDTLineComponents(TypedDict):
    """
    Represents all columns within a line of an SDT file, which contains all parameters for a single note within a chart.
    """
    whole_measures: str
    fraction_measures: str
    note_duration: str
    note_location: str
    note_type: str
    slide_id: str
    slide_pattern: str
    slide_count: str
    slide_delay: str


MeasureStrings = namedtuple("MeasureStrings", ["whole_measures", "fraction_measures"])


class SDTFinaleNote:
    """
    Represents a single note in a Maimai FiNALE chart, as built per the SDT format.

    *TODO: Finish documentation of class, especially parameters.*

    :parameter slide_count: Denotes the number of slides to come out of the slide's star - exclusive to slide stars.
    """

    def __init__(self, note_type: SDTNoteType, note_start_time: float, note_location: int,

                 slide_id: int | None = None, slide_pattern: SDTSlidePattern | None = None,
                 slide_delay: float | None = None,

                 slide_count: int | None = None, note_duration: float | None = None):

        self.__note_location = None
        self.__note_duration = None

        self.note_type: SDTNoteType = note_type
        # TODO: Remember this is split into whole second and fraction
        self.note_start_time: float = note_start_time
        self.note_location: int = note_location
        self.slide_id: int = slide_id
        self.slide_pattern: SDTSlidePattern = slide_pattern
        self.slide_count: int = slide_count

        self.slide_delay: float = slide_delay

        self.note_duration: float = note_duration

    def __str__(self):
        """Returns the note in SDT format, with one space in-between columns."""

        components = (
            *self.get_measure_strings(),
            self.get_note_duration_string(), self.get_note_location_string(), self.get_note_type_string(),
            self.get_slide_id_string(), self.get_slide_pattern_string(),
            self.get_slide_count_string(), self.get_slide_delay_string()
        )

        return " ".join(i+"," for i in components)

    def get_spaced_SDT_string(self, whole_measure_width: int, note_duration_width: int, note_type_width: int, slide_id_width: int, slide_pattern_width: int, slide_count_width: int, slide_delay_width: int):
        """
        Returns the note in SDT format, with columns padded to the widths passed by arguments.
        Columns not given as arguments are always the same width regardless of value when valid.

        :param whole_measure_width:
        :param note_duration_width:
        :param note_type_width:
        :param slide_id_width:
        :param slide_pattern_width:
        :param slide_count_width:
        :param slide_delay_width:
        :return:
        """

        measure_strings = self.get_measure_strings()

        columns = (
            (measure_strings.whole_measures, whole_measure_width),
            (measure_strings.fraction_measures, 6),  # x.xxxx
            (self.get_note_duration_string(), note_duration_width),
            (self.get_note_location_string(), 1),  # 0-7
            (self.get_note_type_string(), note_type_width),
            (self.get_slide_id_string(), slide_id_width),
            (self.get_slide_pattern_string(), slide_pattern_width),
            (self.get_slide_count_string(), slide_count_width),
            (self.get_slide_delay_string(), slide_delay_width),
        )

        return " ".join([f"{str(column[0])+',':<{column[1]+1}}" for idx, column in enumerate(columns)])

        # return (f"{measure_strings.whole_measures:.4f}, {measure_strings.fraction_measures:.4f}, "
        #         f"{self.get_note_duration_string()}, {self.get_note_location_string()}, "
        #         f"{self.note_type.value}, {self.slide_id or 0}, "
        #         f"{self.slide_pattern.value if self.slide_pattern is not None else 0}, "
        #         f"{self.slide_count or 0}, {self.slide_delay or 0:.4f},")

    def get_SDT_line_components(self) -> SDTLineComponents:
        measure_strings = self.get_measure_strings()

        return SDTLineComponents(
            whole_measures=measure_strings.whole_measures, fraction_measures=measure_strings.fraction_measures,
            note_duration=self.get_note_duration_string(), note_location=self.get_note_location_string(),
            note_type=self.get_note_type_string(), slide_id=self.get_slide_id_string(),
            slide_pattern=self.get_slide_pattern_string(), slide_count=self.get_slide_count_string(),
            slide_delay=self.get_slide_delay_string()
        )

    def get_measure_strings(self) -> MeasureStrings:
        whole_measures = math.floor(self.note_start_time)
        fraction_measures = self.note_start_time - whole_measures

        return MeasureStrings(whole_measures=f"{whole_measures:.4f}", fraction_measures=f"{fraction_measures:.4f}")

    def get_note_duration_string(self):
        return f"{self.note_duration or 0:.4f}"

    def get_note_location_string(self):
        return f"{self.note_location}"

    def get_note_type_string(self):
        return f"{self.note_type.value}"

    def get_slide_id_string(self):
        return f"{self.slide_id or 0}"

    def get_slide_pattern_string(self):
        return f"{self.slide_pattern.value if self.slide_pattern is not None else 0}"

    def get_slide_count_string(self):
        return f"{self.slide_count or 0}"

    def get_slide_delay_string(self):
        return f"{self.slide_delay or 0:.4f}"


    @property
    def note_location(self):
        return self.__note_location

    @note_location.setter
    def note_location(self, location: int):
        if not isinstance(location, int):
            raise TypeError(f"`location` must be an `int` (got {type(location)})")

        if not 0 <= location <= 7:
            raise ValueError(f"Note location must be between 0 and 7 (got {location})")

        self.__note_location = location

    @property
    def slide_delay(self):
        return self.__slide_delay

    @slide_delay.setter
    def slide_delay(self, delay):
        if delay is None:
            self.__slide_delay = None
            return
        if not isinstance(delay, float):
            raise TypeError(f"`slide_delay` must be a `float` or `None` (got {type(delay)})")

        if delay < 0:
            raise ValueError("`slide_delay` must be >= 0")

        if delay > 0 and self.note_type != SDTNoteType.START_SLIDE:
            warnings.warn(
                f"`slide_delay` is normally only set for START_SLIDE, while this note is of type {self.note_type.name}. "
                f"Check that this was not done in error before continuing.")
        self.__slide_delay = delay

    @property
    def note_duration(self):
        return self.__note_duration

    @note_duration.setter
    def note_duration(self, note_duration: float | None):
        # No value for the duration field can be assumed for these note types

        if note_duration is None:
            # This *should* be a match case, but that didn't seem to work
            if self.note_type in (SDTNoteType.START_SLIDE, SDTNoteType.HOLD):
                raise ValueError(f"A `note_duration` is required when `type` is `{self.note_type.name}`.")
            elif self.note_type in (SDTNoteType.TAP, SDTNoteType.BREAK, SDTNoteType.SLIDE_STAR):
                self.__note_duration = 0.0625
            elif self.note_type == SDTNoteType.SLIDE_STAR_BREAK:
                self.__note_duration = 0.125
            elif self.note_type == SDTNoteType.END_SLIDE:
                self.__note_duration = 0.0

        elif isinstance(note_duration, float):
            # Handle notes with no known reason to edit durations?
            if self.note_type not in (SDTNoteType.START_SLIDE, SDTNoteType.TAP, SDTNoteType.HOLD):
                warnings.warn(f"`note_duration` is understood to be unused for `{self.note_type.name}`, "
                              f"and a known default is provided. "
                              f"If you did not intend to do this, please check your note construction code.")
            self.__note_duration = note_duration

        else:
            raise TypeError(f"`note_duration` must be a `float` or `None`.")


SDTLine = re.compile(r"^"
                     r"(?P<starting_measure_count>\d+.0000), +"
                     r"(?P<starting_measure_fraction>0.\d{4}), +"
                     r"(?P<note_duration>\d+.\d{4}), +"
                     r"(?P<note_location>[1-8]), +"
                     r"(?P<note_type>[0-5]|128), +"
                     r"(?P<slide_id>\d+), +"
                     r"(?P<slide_pattern>[0-9]|1[0-3]), +"
                     r"(?P<slide_count>\d+), +"
                     r"(?P<slide_delay>\d+.\d{4}),"
                     r"$"
                     )


def read_SDT_file(path: str) -> list[SDTFinaleNote]:
    notes = []

    with open(path, "r") as f:
        for count, line in enumerate(f):
            match = SDTLine.match(line)
            if not match:
                print(f"Couldn't parse line {count}: {line}")

            else:
                pattern_id = int(match.group("slide_pattern"))
                if pattern_id != 0:
                    pattern = SDTSlidePattern(pattern_id)
                else:
                    pattern = None
                notes.append(SDTFinaleNote(
                    note_type=SDTNoteType(int(match.group("note_type"))),
                    note_start_measures=float(match.group("starting_measure_count")),
                    note_start_measure_fraction=float(match.group("starting_measure_fraction")),
                    note_location=int(match.group("note_location")),
                    slide_id=int(match.group("slide_id")),
                    slide_pattern=pattern,
                    slide_delay=float(match.group("slide_delay")),
                    slide_count=int(match.group("slide_count")),
                    note_duration=float(match.group("note_duration")),
                ))

        return notes


class FinaleNote:
    ...

