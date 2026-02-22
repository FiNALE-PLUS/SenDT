import warnings

from colorama import Fore, Style

from errors.chart import ChartWarning, ChartFeatureWarning, ChartUserWarning
from errors.sentakki_simai import SentakkiCommentWarning


def chart_warn(message: str, chart_fragment: str, chart_time: float, line_num: int,
               warning_type: type[ChartWarning] = ChartWarning):
    warnings.warn(
        Fore.YELLOW +
        f"{message} (chart fragment: {chart_fragment} at "
        f"{chart_time:.3f}s [line {line_num + 1}])"
        + Style.RESET_ALL,
        warning_type,
        stacklevel=3,
    )


def chart_feature_warn(message: str, chart_fragment: str, chart_time: float, line_num: int):
    return chart_warn(message, chart_fragment, chart_time, line_num, ChartFeatureWarning)


def chart_user_warn(message: str, chart_fragment: str, chart_time: float, line_num: int):
    return chart_warn(message, chart_fragment, chart_time, line_num, ChartUserWarning)


def sentakki_comment_warn(message: str, key: str, value: str, line_num: int):
    warnings.warn(
        Fore.YELLOW +
        f"{message} (sentakki comment: key - `{key}`, value - `{value}` [line {line_num}])"
        + Style.RESET_ALL,
        SentakkiCommentWarning,
        stacklevel=3,
    )


def redefined_comment_value_warn(value_type: str, predefined_value: str, key: str, value: str, line_num: int):
    return sentakki_comment_warn(f"A {value_type} has already been defined for this chart. "
                                 f"It will be kept as the first defined value of `{predefined_value}`.",
                                 key, value, line_num
                                 )
