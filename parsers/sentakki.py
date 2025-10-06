import gzip
import os
import re
import sys
import warnings
from binascii import unhexlify
from io import StringIO
from pathlib import Path
from pprint import pprint
from typing import Union, NamedTuple, TypedDict
from unittest import case

from Crypto.Cipher import AES
from colorama import Style, Fore

from dialects.abstract.finale import FinaleNote, SDTFinaleNote, SDTNoteType, SDTSlidePattern
from environment_vars import CRYPT_KEY
from errors.chart import ChartDialectError, ChartDialect, ChartFeatureWarning, ChartWarning, ChartError, \
    ChartGrandVError, ChartSlideError, ChartSlidePathError, InvalidReturningSlidePatternError

from fractions import Fraction

from parsers.sentakki_sdt.errors.parsing import InvalidSlideNote
from parsers.sentakki_sdt.slides import get_slide_count_in_separated_slide_slot, get_slide_path_params, \
    parse_sentakki_slide_note, get_button_slide_counts_from_note_slot
from parsers.simai_utils.chart import simai_to_SDT_note_position
from parsers.simai_utils.timing import measures_to_seconds, seconds_to_measures
from parsers.simai_utils.warnings import chart_feature_warn
from parsers.regex_patterns.sentakki import *


def get_cur_time_from_timing_dict(timing_dict: dict) -> float:
    total_time = 0.0

    for bpm in timing_dict:
        for divider, count in timing_dict[bpm].items():
            # Time signature is assumed to be 4/4, so a divider of 4 is at the rate of the BPM
            total_time += count * (60 / (bpm * (divider / 4)))

    return total_time


def get_chart_bpm(chart: str):
    bpm = -1
    for line in chart.splitlines():
        if bpm_match := bpm_re.match(line):
            bpm = float(bpm_match.group("bpm"))

    if bpm == -1:
        raise ChartError("No BPM marker in chart.")

    return bpm

            #chart_bpm / (cur_bpm * length_divider)

    cur_measures += chart_bpm / (cur_bpm * length_divider)
            #seconds * (chart_bpm / (cur_bpm * 4))
            # ((seconds * bpm) / 60) / (cur_divider / 4)

# def measures_():
#     return chart_bpm / (cur_bpm * length_divider)


# TODO: allow for rounding to the closest beat fraction
def round_measure_from_sentakki_accuracy(seconds: float, bpm: float, divider: int):
    # Sentakki goes to 3dp, so this should be the max difference from error (within reason)
    margin: float = bpm * (0.00099 / 60)

    rounded_measure = round(seconds)


def parse_sentakki_slide_note_slot(note: str, note_match: re.Match, combined: bool,
                                   cur_chart_seconds: float, line_number: int) -> list[SDTFinaleNote]:
    ...
    # TODO: Add function to move slide note logic to its own function
    #  (Regex encompassing combined and not combined? if-else?)


def parse_sentakki_finale_chart(chart: str, chart_bpm: float | None = None) -> tuple[list[SDTFinaleNote], dict[str, str]]:
    # TODO: Slide timing and delays are incorrect - look into conversions from seconds to measures, and also how sentakki exports slides
    #  Slide timings are in seconds.

    notes: list[SDTFinaleNote] = []
    # cur_timing = {}

    comments = {}

    if chart_bpm is None:
        chart_bpm = get_chart_bpm(chart)
        # chart_bpm = 30.0
        print(f"Chart BPM detected: {chart_bpm} - Use this for tables. (All notes at other BPMs will be adjusted to match)")
    else:
        print(f"Using selected BPM for chart: {chart_bpm} - Use this for tables. (All notes at other BPMs will be adjusted to match)")
    cur_bpm = chart_bpm
    cur_measures = 0.0

    length_divider = -1

    cur_slide_id = 1

    # print(chart)

    first_line = True

    chart_lines = chart.splitlines()

    for line_number, line in enumerate(chart_lines):
        if line.startswith("&"):
            comment_and_value = line[1:].split("=")
            comments[comment_and_value[0]] = comment_and_value[1]
        else:
            chart_line = line

            # Check for BPM change
            if bpm_match := bpm_re.match(line):
                cur_bpm = float(bpm_match.group("bpm"))
                # print(f"Changed BPM to: {cur_bpm} (Line: {line})")
                # Account for trailing bracket that isn't part of the match
                chart_line = chart_line[bpm_match.end("bpm") + 1:]

            # Get current beat length division
            if divider_match := length_divider_re.match(chart_line):
                length_divider = int(divider_match.group("length_divider"))
                # Account for trailing brace
                chart_line = chart_line[divider_match.end("length_divider") + 1:]
            # else:
            #     raise ChartDialectError(ChartDialect.Sentakki,
            #                             "Sentakki charts always have a length divider at the beginning of a line.",
            #                             line)

            if chart_line:
                line_notes = chart_line.split(",")[:-1]
                # if first_line:
                #     line_notes = line_notes[1:]
                #     first_line = False
                # Represents all notes at a specific point in the chart
                for note_slot in line_notes:
                    slot_has_slide = False

                    # if cur_bpm not in cur_timing:
                    #     cur_timing[cur_bpm] = {}
                    # if length_divider not in cur_timing[cur_bpm]:
                    #     cur_timing[cur_bpm][length_divider] = 0
                    # cur_timing[cur_bpm][length_divider] += 1

                    cur_chart_time = cur_measures
                    zone_slide_counts = get_button_slide_counts_from_note_slot(note_slot)

                    # print(cur_chart_measures, note_slot)

                    # Necessary to split chord notes
                    split_slot = note_slot.split("/")
                    for note in split_slot:
                        if note:
                            if tap_match := tap_note_re.match(note):
                                location = simai_to_SDT_note_position(tap_match.group("location"))
                                is_break = False
                                is_star = False

                                note_type = SDTNoteType.TAP

                                flags = tap_match.group("flags")
                                if flags is not None:
                                    is_break = "b" in flags
                                    is_star = "$" in flags

                                if is_break and is_star:
                                    note_type = SDTNoteType.SLIDE_STAR_BREAK
                                elif is_break:
                                    note_type = SDTNoteType.BREAK
                                elif is_star:
                                    note_type = SDTNoteType.SLIDE_STAR

                                notes.append(
                                    SDTFinaleNote(
                                        note_type=note_type,
                                        note_start_time=cur_chart_time,
                                        note_location=location,
                                    )
                                )

                            elif hold_match := hold_note_re.match(note):

                                if hold_match.group("break"):
                                    chart_feature_warn("A hold note has been added as a break. This is not possible in "
                                                       "FiNALE, and will not be encoded as such.", note,
                                                       measures_to_seconds(cur_chart_time, chart_bpm),
                                                       line_number)

                                location = (int(hold_match.group("location")) - 1) % 8
                                duration = float(hold_match.group("duration"))

                                # Assumes final BPM is used for the whole chart
                                notes.append(
                                    SDTFinaleNote(
                                        note_type=SDTNoteType.HOLD,
                                        note_start_time=cur_chart_time,
                                        note_location=location,
                                        note_duration=seconds_to_measures(duration, chart_bpm, cur_bpm),
                                    )
                                )

                            # Redundant, but in return vastly simplifies unrecognised notes
                            elif full_slide_note_re.match(note) or combined_slide_note_re.match(note):
                                try:
                                    slide_note_components, new_slide_id = parse_sentakki_slide_note(
                                        note, cur_slide_id, zone_slide_counts,
                                        cur_measures, chart_bpm, cur_bpm, line_number,
                                    )
                                except InvalidSlideNote:  # No slide note found
                                    print("Slide note found as invalid.", note_slot)
                                else:
                                    notes.extend(slide_note_components)
                                    cur_slide_id = new_slide_id

                            else:
                                print(
                                    Fore.LIGHTCYAN_EX +
                                    f"Unrecognised note: {note} (Chart time: {measures_to_seconds(cur_chart_time, chart_bpm)}s, Line number: {line_number})"
                                    + Style.RESET_ALL,
                                )

                    # Assumes 4:4
                    # Move to next timing "slot" AFTER the note is added
                    cur_measures += chart_bpm / (cur_bpm * length_divider)

                # print(line, chart_line, line_notes)

    # pprint(comments)

    return sorted(notes, key=lambda n: n.note_start_time), comments


def parse_sentakki_finale_file(path: str, chart_bpm: float | None = None):
    with open(path, "r", encoding="utf-8") as f:
        return parse_sentakki_finale_chart(f.read(), chart_bpm)


def convert_sentakki_file_to_SDT_string(input_path: str, pad_columns: bool, chart_bpm: float | None = None):
    SDT_notes, comments = parse_sentakki_finale_file(input_path, chart_bpm)

    # Generate chart contents
    chart_string: str = ""

    if pad_columns:
        max_whole_measure_width = 0
        max_note_duration_width = 0
        max_note_type_width = 0
        max_slide_id_width = 0
        max_slide_pattern_width = 0
        max_slide_count_width = 0
        max_slide_delay_width = 0

        for note in SDT_notes:
            if (whole_measure_width := len(note.get_measure_strings().whole_measures)) > max_whole_measure_width:
                max_whole_measure_width = whole_measure_width
            if (note_duration_width := len(note.get_note_duration_string())) > max_note_duration_width:
                max_note_duration_width = note_duration_width
            if (note_type_width := len(note.get_note_type_string())) > max_note_type_width:
                max_note_type_width = note_type_width
            if (slide_id_width := len(note.get_slide_id_string())) > max_slide_id_width:
                max_slide_id_width = slide_id_width
            if (slide_pattern_width := len(note.get_slide_pattern_string())) > max_slide_pattern_width:
                max_slide_pattern_width = slide_pattern_width
            if (max_slide_count_width := len(note.get_slide_count_string())) > max_slide_count_width:
                max_slide_count_width = max_slide_count_width
            if (max_slide_delay_width := len(note.get_slide_count_string())) > max_slide_delay_width:
                max_slide_delay_width = max_slide_delay_width

        for note in SDT_notes:
            chart_string += note.get_spaced_SDT_string(
                whole_measure_width=max_whole_measure_width, note_duration_width=max_note_duration_width,
                note_type_width=max_note_type_width, slide_id_width=max_slide_id_width,
                slide_pattern_width=max_slide_pattern_width,
                slide_count_width=max_slide_count_width, slide_delay_width=max_slide_delay_width
            ) + "\n"

    else:
        for note in SDT_notes:
            chart_string += str(note)+"\n"

    return chart_string


def write_SDT_string_to_SDB_file(path: str, chart_string: str):
    out = Path(path)

    with open(out.with_suffix(".sdb"), "wb") as f:
        f.write(finale_encrypt(CRYPT_KEY, bytes(chart_string, encoding="ascii")))

def convert_sentakki_file_to_SDB_file(input_path: str, output_path: str, pad_columns: bool, chart_bpm: float | None = None):
    chart_string: str = convert_sentakki_file_to_SDT_string(input_path, pad_columns, chart_bpm)

    write_SDT_string_to_SDB_file(output_path, chart_string)


# https://github.com/donmai-me/MaiConverter/blob/master/maiconverter/maicrypt/maifinalecrypt.py

def finale_encrypt(
    key: Union[str, bytes],
    plaintext: bytes,
) -> bytes:
    if not isinstance(key, bytes):
        key = int(key.replace(" ", ""), 0).to_bytes(0x10, "big")
    if len(key) != 0x10:
        raise ValueError("Invalid key length")

    JUNK = unhexlify("4b67ca1eebc78fb9964f781019bc4903")
    encoded = JUNK + plaintext

    gzipdata = gzip.compress(encoded)
    if len(gzipdata) % 0x10 != 0:
        amount = 0x10 - (len(gzipdata) % 0x10)
        padding = amount.to_bytes(1, "big") * amount
        gzipdata += padding

    iv = os.urandom(0x10)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    return iv + cipher.encrypt(gzipdata)
