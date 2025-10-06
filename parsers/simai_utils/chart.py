from pathlib import Path
from typing import LiteralString

from parsers.regex_patterns.sentakki import bpm_re


def simai_to_SDT_note_position(position: int | str) -> int:
    if isinstance(position, str):
        position = int(position)

    if position < 1 or position > 8:
        raise ValueError(f"Simai note position must be between 1 and 8 (got {position})")

    return (position - 1) % 8


def get_chart_bpms(chart_path: Path) -> list[float]:
    bpms = set()

    with open(chart_path, "r", encoding="utf-8") as f:
        chart_lines = f.read().splitlines()

    for line in chart_lines:
        if bpm_match := bpm_re.match(line):
            bpms.add(float(bpm_match.group("bpm")))

    return sorted(bpms)
