import re
from pathlib import Path
from pprint import pprint

from tableUI.parsers.parse import parse_plain_textout
from tableUI.parsers.tables.field_types.quoted_string import TextoutQuotedString
from tableUI.parsers.tables.textout.models import TextoutRow, UnfilledTextoutExTable

song_info_key_pattern = re.compile(r'(?P<song_title>RST_MUSICTITLE_(?P<song_id>\d{4}))'
                                   r'|(?P<song_artist>RST_MUSICARTIST_(?P<song_artist_id>\d{4}))'
                                   r'|(?P<chart_creator>RST_SCORECREATOR_(?P<chart_creator_id>\d{4}))')
