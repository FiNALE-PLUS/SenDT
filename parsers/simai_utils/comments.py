import re
from typing import TypedDict, Required

from parsers.simai_utils.identifiers.comments import SentakkiCommentKeys, SentakkiCommentValues
from parsers.simai_utils.warnings import sentakki_comment_warn, redefined_comment_value_warn
from utils.finale.difficulties import FinaleChartDifficulty, FinaleUtageType


comment_line = re.compile(
    r"^&(?P<key>\w+)="

    r"(?P<value>"
    r"(?P<int_value>\d+)"
    r"|(?P<float_value>\d+[.]\d+?)"
    r"|(?P<string_value>.+))?$"
)

chart_difficulty_re = re.compile(
    r"^lv_(?P<chart_level>\d+)$"
)


# Extra requirements for mmMusic
class FinaleMusicParameters(TypedDict, total=True):
    song_id: Required[int | None]
    song_safename: Required[str | None]
    bpm: Required[float | None]


# Requirements for mmTextout
class FinaleTextOutParameters(TypedDict, total=True):
    song_title: Required[str]
    song_artist: Required[str]
    chart_author: Required[str]


# Requirements for individual charts in mmScore + sentakki heuristic
class SentakkiChartParameters(FinaleTextOutParameters, total=True):
    difficulty_level: Required[FinaleChartDifficulty]
    difficulty_value: Required[float | None]
    utage_type: Required[FinaleUtageType | None]
    is_sentakki: Required[bool]


class FinaleChartParameters(FinaleTextOutParameters, SentakkiChartParameters):
    pass


class FinaleExportParameters(FinaleMusicParameters, FinaleChartParameters):
    pass


def parse_sentakki_chart_parameters_from_comments(chart_lines: list[str]) -> SentakkiChartParameters:
    song_title: str | None = None
    song_artist: str | None = None
    song_author: str | None = None
    chart_difficulty_level: FinaleChartDifficulty | None = None
    chart_difficulty_value: float | int | None = None
    chart_utage_type: FinaleUtageType | None = None
    is_sentakki = False

    for line_num, line in enumerate(chart_lines, start=1):
        if comment_match := comment_line.match(line):
            comment_key = comment_match.group("key")
            comment_value = comment_match.group("value")

            match comment_key:
                case SentakkiCommentKeys.SENTAKKI_IDENTIFIER:
                    if comment_value == SentakkiCommentValues.SENTAKKI_IDENTIFIER_COMMENT:
                        is_sentakki = True
                    else:
                        ...
                    continue
                case SentakkiCommentKeys.SONG_TITLE:
                    if song_title is None:
                        song_title = comment_value
                    else:
                        redefined_comment_value_warn("song safename", song_title,
                                                     comment_key, comment_value,
                                                     line_num)
                    continue
                case SentakkiCommentKeys.SONG_ARTIST:
                    if song_artist is None:
                        song_artist = comment_value
                    else:
                        redefined_comment_value_warn("song artist", song_artist,
                                                     comment_key, comment_value,
                                                     line_num)
                    continue
                case SentakkiCommentKeys.CHART_AUTHOR:
                    if song_author is None:
                        song_author = comment_value
                    else:
                        redefined_comment_value_warn("song author", song_author,
                                                     comment_key, comment_value,
                                                     line_num)
                    continue

            if diff_match := chart_difficulty_re.match(comment_key):
                if chart_difficulty_level is not None:
                    raise NotImplementedError("Multiple difficulty levels have been declared "
                                              "within this simai file. senDT does not currently support "
                                              "multiple charts within the same file "
                                              "(but is intended for future implementation).")

                difficulty_id = int(diff_match.group("chart_level"))

                parsed_difficulty, parsed_utage_type, parsed_difficulty_value = parse_sentakki_difficulty_comment(
                    difficulty_id, comment_key, comment_value, line_num
                )

                if parsed_difficulty is not None:
                    chart_difficulty_level, chart_utage_type, chart_difficulty_value \
                        = parsed_difficulty, parsed_utage_type, parsed_difficulty_value

                else:
                    sentakki_comment_warn("The difficulty level of the chart is not a valid FiNALE difficulty ID. "
                                          "Please check the simai file and correct the difficulty comment.",
                                          comment_key, comment_value, line_num)

    return SentakkiChartParameters(
        song_title=song_title,
        song_artist=song_artist,
        chart_author=song_author,
        difficulty_level=chart_difficulty_level,
        difficulty_value=chart_difficulty_value,
        utage_type=chart_utage_type,
        is_sentakki=is_sentakki,
    )


def parse_sentakki_difficulty_comment(difficulty_id: int, comment_key: str, comment_value: str,
                                      line_num: int) -> tuple[FinaleChartDifficulty | None, FinaleUtageType | None, int | None]:
    chart_difficulty = None
    chart_utage_type = None
    chart_difficulty_value = None
    if difficulty_id == 7:
        sentakki_comment_warn("The difficulty ID has been left as the default value (7). "
                              "This is not a valid FiNALE ID, and should be changed. "
                              "(A future behaviour change may occur)",
                              comment_key, comment_value, line_num)
        return None, None, None
    else:
        for difficulty in FinaleChartDifficulty:
            if difficulty.value == difficulty_id:
                chart_difficulty = difficulty
                break

    if chart_difficulty is not None:
        # Valid Utage difficulty
        if 'UTAGE' in chart_difficulty.name:

            if comment_value is None:
                sentakki_comment_warn("No utage type has been defined for the chart. "
                                      "Please check and correct the difficulty comment.",
                                      comment_key, comment_value, line_num)

            else:
                for utage_type in FinaleUtageType:
                    # Case insensitive for english name
                    if comment_value.upper() in (str(utage_type.id), utage_type.name, utage_type.kanji):
                        chart_utage_type = utage_type
                        break
                if chart_utage_type is None:
                    sentakki_comment_warn("No valid utage type has been declared for a chart "
                                          "which is declared to use an utage slot.",
                                          comment_key, comment_value, line_num)

        else:
            try:
                parsed_difficulty_value = float(comment_value)

                if parsed_difficulty_value < 1 or parsed_difficulty_value > 14:
                    raise ValueError("Non-utage difficulty value must be between 1 and 14 inclusive.")

                if round(parsed_difficulty_value) == parsed_difficulty_value:
                    chart_difficulty_value = int(parsed_difficulty_value)
                else:
                    chart_difficulty_value = parsed_difficulty_value
            except ValueError:
                sentakki_comment_warn("An invalid difficulty value has been declared for a non-utage chart. "
                                      "Please check and correct the chart's declared difficulty.",
                                      comment_key, comment_value, line_num)
            except TypeError:
                sentakki_comment_warn("No difficulty value has been declared for a non-utage chart. "
                                      "Please check and correct the chart's declared difficulty.",
                                      comment_key, comment_value, line_num)

    return chart_difficulty, chart_utage_type, chart_difficulty_value
