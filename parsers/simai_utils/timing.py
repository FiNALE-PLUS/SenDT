import warnings
from fractions import Fraction


def measures_to_seconds(measures: float, chart_bpm: float):
    return (1 / chart_bpm) * 60 * 4 * measures

def seconds_to_measures(seconds: float, chart_bpm: float, cur_bpm: float):

    if seconds == 0:
        warnings.warn("Found 0 length note.")
        return 0.0

    relative_bpm = (chart_bpm / cur_bpm) * chart_bpm

    total_beats = (relative_bpm / (60 / seconds))

    # print(f"Total beats: {total_beats}")

    beats_fraction = Fraction(total_beats)

    nearest_16th_beat = beats_fraction.limit_denominator(16)

    nearest_beat_difference = abs(nearest_16th_beat - total_beats)

    if nearest_beat_difference < 0.001:
        # print(f"Nearest beat within error, rounding... (total_beats: {total_beats},", end="")
        # Cast to a float for simplicity - Fraction functionality is no longer needed
        total_beats = float(nearest_16th_beat)
        # print(f" rounded total_beats: {total_beats})")

    # Assumes 4:4
    total_measures = total_beats / 4



    length_divider = 0

    return total_measures