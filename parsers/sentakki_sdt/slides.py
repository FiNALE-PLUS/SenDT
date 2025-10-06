from typing import TypedDict

from dialects.abstract.finale import SDTFinaleNote, SDTSlidePattern, SDTNoteType

from re import Match

from errors.chart import ChartGrandVError, InvalidReturningSlidePatternError
from parsers.regex_patterns.sentakki import full_slide_note_re, combined_slide_note_re, slide_patterns_re, slide_path_re
from parsers.sentakki_sdt.errors.parsing import InvalidSlideNote
from parsers.simai_utils.chart import simai_to_SDT_note_position
from parsers.simai_utils.timing import measures_to_seconds, seconds_to_measures
from parsers.simai_utils.warnings import chart_feature_warn

class SDTSlideParams(TypedDict):
    start_location: int
    end_location: int
    pattern: SDTSlidePattern
    delay_seconds: float
    duration_seconds: float

def get_slide_count_in_separated_slide_slot(note_slot: str):
    slide_count = 0

    notes_in_slot = note_slot.split("/")
    for note in notes_in_slot:
        if slide_patterns_re.search(note) is not None:
            slide_count += 1

    return slide_count

def get_SDT_slide_type(sentakki_slide_type: str, start_location: int, end_location: int):
    # TODO: Output note timings as measures instead of seconds
    match sentakki_slide_type:
        case "-":
            return SDTSlidePattern.STRAIGHT_LINE
        case "q":
            return SDTSlidePattern.INNER_ARC_CW
        case "p":
            return SDTSlidePattern.INNER_ARC_CCW
        case "s":
            return SDTSlidePattern.ZIGZAG_S
        case "z":
            return SDTSlidePattern.ZIGZAG_Z
        case "v":
            return SDTSlidePattern.V_CENTER_END
        case "qq":
            return SDTSlidePattern.STRAIGHT_CENTER_ARC_CW
        case "pp":
            return SDTSlidePattern.STRAIGHT_CENTER_ARC_CCW
        case "w":
            return SDTSlidePattern.FAN
        case "<" | ">" | "^":
            return get_circle_slide_pattern(sentakki_slide_type, start_location, end_location)
    # Grand V is handled independently of this function
    raise ValueError(f"No SDT slide pattern for '{sentakki_slide_type}'")


def get_circle_slide_pattern(sentakki_slide_type: str, start_location: int, end_location: int):
    assert sentakki_slide_type in ("<", ">", "^")
    assert start_location >= 0 <= 7
    assert end_location >= 0 <= 7

    length = abs(start_location - end_location)

    if sentakki_slide_type == "^":
        print(f"This slide pattern character has not been tested (`^`). Please report to the developer if this functions as intended.")
        assert 1 <= length <= 3
        if length != start_location - end_location:
            return SDTSlidePattern.OUTER_CIRCLE_CW
        else:
            return SDTSlidePattern.OUTER_CIRCLE_CCW

    else:
        # Arrow indicates left or right from start point - these startpoints have the arrows mean the opposite (-1 for SDT format)
        SDT_invert_direction_start_idxs = (2, 3, 4, 5)

        if sentakki_slide_type == ">":
            clockwise = True
        else:
            clockwise = False

        if start_location in SDT_invert_direction_start_idxs:
            clockwise = not clockwise

        return SDTSlidePattern.OUTER_CIRCLE_CW if clockwise else SDTSlidePattern.OUTER_CIRCLE_CCW

def get_slide_path_params(slide_match: Match, start_location: int | None = None) -> SDTSlideParams:

    if start_location is None:
        start_location = simai_to_SDT_note_position(int(slide_match.group("start_location")))
        if start_location is None:
            raise ValueError("No start location provided.")

    if slide_match.group("grand_v_end_location"):
        midpoint = simai_to_SDT_note_position(int(slide_match.group("grand_v_midpoint")))
        end_location = simai_to_SDT_note_position(int(slide_match.group("grand_v_end_location")))

        position_difference = (start_location - midpoint) % 8

        # Find whether the midpoint is clockwise or counter-clockwise
        # from the start of the slide
        if position_difference == 6:
            note_SDT_slide_pattern = SDTSlidePattern.START_CW_TWO_END
        elif position_difference == 2:
            note_SDT_slide_pattern = SDTSlidePattern.START_CCW_TWO_END
        else:
            raise ChartGrandVError("Invalid midpoint for Grand V")
    else:
        end_location = simai_to_SDT_note_position(int(slide_match.group("end_location")))
        note_SDT_slide_pattern = get_SDT_slide_type(slide_match.group("slide_pattern"), start_location, end_location)

    if start_location == end_location and note_SDT_slide_pattern not in (
            SDTSlidePattern.OUTER_CIRCLE_CCW, SDTSlidePattern.OUTER_CIRCLE_CW,
            SDTSlidePattern.INNER_ARC_CCW, SDTSlidePattern.INNER_ARC_CW,
            SDTSlidePattern.V_CENTER_END,
            SDTSlidePattern.STRAIGHT_CENTER_ARC_CCW, SDTSlidePattern.STRAIGHT_CENTER_ARC_CW,
    ):
        raise InvalidReturningSlidePatternError(note_SDT_slide_pattern)

    return SDTSlideParams(
        start_location=start_location, end_location=end_location, pattern=note_SDT_slide_pattern,
        delay_seconds=float(slide_match.group("delay")), duration_seconds=float(slide_match.group("duration")),
    )


def get_button_slide_counts_from_note_slot(note_slot: str) -> list[int]:
    """
    Returns the number of slides that begin at each zone of the screen.

    :param note_slot:
    :return:
    """

    split_note_slot = note_slot.split("/")

    slide_counts = [0 for _ in range(8)]

    for note in split_note_slot:
        if combined_slide_match := combined_slide_note_re.match(note):
            slide_counts[simai_to_SDT_note_position(combined_slide_match.group("start_location"))] += len(note.split("*"))
        elif slide_match := full_slide_note_re.match(note):
            slide_counts[simai_to_SDT_note_position(slide_match.group("start_location"))] += 1

    return slide_counts


def parse_sentakki_slide_note(note: str, cur_slide_id: int, zone_slide_counts: list[int],
                              cur_chart_measures: float, chart_bpm: float, cur_bpm: float,
                              line_number: int) -> tuple[list[SDTFinaleNote], int]:
    slide_note_components = []

    slide_match = full_slide_note_re.match(note)
    combined_slide_match = combined_slide_note_re.match(note)

    if not combined_slide_match and not slide_match:
        raise InvalidSlideNote("This note does not match any known slide pattern.")

    matched_note = combined_slide_match if combined_slide_match else slide_match

    start_location = (int(matched_note.group("start_location")) - 1) % 8
    delay = float(matched_note.group("delay"))
    duration = float(matched_note.group("duration"))

    note_SDT_slide_pattern: SDTSlidePattern

    if matched_note.group("break_slide"):
        chart_feature_warn("This slide note uses a break slide out_path. "
                           "This is not possible in FiNALE, "
                           "and will not be encoded as such.",
                           note, measures_to_seconds(cur_chart_measures, chart_bpm), line_number)

    try:
        if slide_match:
            if not slide_match.group("omit_star"):

                slide_star_tap = SDTFinaleNote(
                    note_type=
                    SDTNoteType.SLIDE_STAR if not matched_note.group("break_star")
                    else SDTNoteType.SLIDE_STAR_BREAK,
                    note_start_time=cur_chart_measures,
                    note_location=start_location,
                    slide_count=zone_slide_counts[start_location]
                )
                slide_note_components.append(slide_star_tap)

            slide_path_params_list = [get_slide_path_params(slide_match, start_location)]
        else:  # combined slide
            split_slide = note.split("*")
            slide_count = len(split_slide)

            slide_path_params_list = []

            for idx, split_note in enumerate(split_slide):
                if idx == 0:
                    note_match = full_slide_note_re.match(split_note)

                    start_location = simai_to_SDT_note_position(note_match.group("start_location"))
                    assert start_location is not None

                    if not note_match.group("omit_star"):
                        # Initial Star
                        slide_star_tap = SDTFinaleNote(
                            note_type=
                            SDTNoteType.SLIDE_STAR if not note_match.group("break_star")
                            else SDTNoteType.SLIDE_STAR_BREAK,
                            note_start_time=cur_chart_measures,
                            note_location=start_location,
                            slide_count=slide_count
                        )

                        slide_note_components.append(slide_star_tap)

                else:
                    assert start_location is not None
                    note_match = slide_path_re.match(split_note)

                slide_path_params_list.append(get_slide_path_params(note_match, start_location))


    except ValueError:
        chart_feature_warn(
            "Couldn't parse a start location for this slide. "
            "Contact the developer about this error.",
            note, measures_to_seconds(cur_chart_measures, chart_bpm), line_number
        )
        return [], cur_slide_id
    except ChartGrandVError:
        chart_feature_warn("This slide note seems to be an incorrectly placed grand V. "
                           "The midpoint for a grand V is always 2 positions away "
                           "from the beginning of the slide. "
                           "This note will not be encoded.",
                           note, measures_to_seconds(cur_chart_measures, chart_bpm), line_number)
        return [], cur_slide_id
    except InvalidReturningSlidePatternError as e:
        chart_feature_warn(f"Slide start and end locations MUST be different for "
                           f"{e.slide_pattern.name}. "
                           "This note will not be encoded.",
                           note, measures_to_seconds(cur_chart_measures, chart_bpm), line_number)
        return [], cur_slide_id
    else:

        for slide_path_params in slide_path_params_list:
            end_location = slide_path_params["end_location"]
            note_SDT_slide_pattern = slide_path_params["pattern"]
            # Slide start note
            slide_note_components.append(SDTFinaleNote(
                note_type=SDTNoteType.START_SLIDE,
                note_start_time=cur_chart_measures,
                note_location=start_location,
                # In seconds, so independent of the note divisor currently in place
                note_duration=seconds_to_measures(duration, chart_bpm, cur_bpm),
                slide_id=cur_slide_id,
                slide_pattern=note_SDT_slide_pattern,
                slide_delay=seconds_to_measures(delay, chart_bpm, cur_bpm),
            ))

            # print(delay)
            # print(seconds_to_measures(delay, chart_bpm, cur_bpm))

            # Slide end note
            slide_note_components.append(SDTFinaleNote(
                note_type=SDTNoteType.END_SLIDE,
                note_start_time=cur_chart_measures + seconds_to_measures(duration + delay, chart_bpm, cur_bpm),
                note_location=end_location,
                slide_id=cur_slide_id,
                slide_pattern=note_SDT_slide_pattern,
            ))
            cur_slide_id += 1

    return slide_note_components, cur_slide_id
