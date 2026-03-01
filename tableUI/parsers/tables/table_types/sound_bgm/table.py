from pathlib import Path

from sqlmodel import Session, select

from db.models import Song
from tableUI.parsers.tables.field_types.quoted_string import DoubleQuotedString

HARDCODED_ROWS = r"""
TUTORIAL, 026,
TUTORIAL_EN, 074,
OMAKASE, 430,
""".strip() + '\n'


def build_soundbgm_from_session(session: Session) -> str:
    ordered_songs = session.exec(
        select(Song).
        order_by(Song.filename.asc())
    ).all()

    soundbgm_content = HARDCODED_ROWS
    for song in ordered_songs:
        soundbgm_content += f'\n{','.join((DoubleQuotedString.remove_quotes(song.filename), f"{song.id:03}"))}'

    return soundbgm_content


def write_session_soundbgm_to_path(session: Session, path: Path) -> None:
    cur_soundbgm_content = build_soundbgm_from_session(session)

    # Specify UTF-8 to ensure parity with original
    with open(path, 'w', encoding='utf-8') as f:
        f.write(cur_soundbgm_content)
